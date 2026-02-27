from models.machine import Machine
from models.factory_log import FactoryLog
from models.daily_machine_kpi import DailyMachineKpi
from models.machine_alert import MachineAlert
from config import db
from datetime import date, datetime

# ============================================================
# SEUILS
# ============================================================
SEUIL_AVAILABILITY_WARN  = 0.80   # en dessous = warning
SEUIL_AVAILABILITY_CRIT  = 0.60   # en dessous = critical
SEUIL_ANOMALY_WARN       = 0.10   # 10% anomalies = warning
SEUIL_ANOMALY_CRIT       = 0.25   # 25% anomalies = critical
SEUIL_UTILIZATION_WARN   = 0.50   # en dessous = sous-utilisée
COUT_PANNE_UNITAIRE      = 150.0  # coût estimé par panne en €


# ============================================================
# FONCTION PRINCIPALE
# ============================================================
def calculer_et_stocker_machine_kpi():
    today = date.today()
    machines = Machine.query.all()

    if not machines:
        print("[Machine Scheduler] ⚠️ Aucune machine trouvée")
        return

    for machine in machines:
        kpi = _calculer_kpi_machine(machine, today)
        if kpi:
            _upsert_daily_machine_kpi(kpi, machine.machine_id, today)
            _generer_alertes(kpi, machine, today)

    db.session.commit()
    print(f"[Machine Scheduler] ✅ KPI calculés pour {today} à {datetime.now().strftime('%H:%M:%S')}")


# ============================================================
# CALCUL KPI PAR MACHINE
# ============================================================
def _calculer_kpi_machine(machine, today):
    try:
        # Tous les logs de cette machine
        logs = FactoryLog.query.filter_by(machine_id=machine.machine_id).all()
        logs_today = [
            l for l in logs
            if l.tag_event_start and l.tag_event_start[:10] == str(today)
        ]

        total_logs   = len(logs_today)
        total_anomalies = sum(1 for l in logs_today if l.anomaly_flag == 1)

        # --- Anomaly Rate ---
        anomaly_rate = round(
            total_anomalies / total_logs, 4
        ) if total_logs > 0 else 0.0

        # --- Availability ---
        # etat_machine : 'Opérationnelle' = disponible
        availability = 1.0 if machine.etat_machine == "Opérationnelle" else 0.0

        # --- Utilization Rate ---
        # tâches actives aujourd'hui / capacité machine
        utilization_rate = round(
            total_logs / machine.capacite, 4
        ) if machine.capacite > 0 else 0.0
        # plafonner à 1.0
        utilization_rate = min(utilization_rate, 1.0)

        # --- MTBF ---
        # heures disponibles par mois / nombre de pannes
        heures_mois = 160.0
        mtbf = round(
            heures_mois / machine.pannes_mois, 2
        ) if machine.pannes_mois > 0 else heures_mois

        # --- MTTR ---
        # estimé : 10% du MTBF comme proxy
        mttr = round(mtbf * 0.10, 2)

        # --- Cost Estimate ---
        cost_estimate = round(machine.pannes_mois * COUT_PANNE_UNITAIRE, 2)

        return {
            "machine_id":       machine.machine_id,
            "nom_machine":      machine.nom_machine,
            "atelier":          machine.atelier,
            "etat_machine":     machine.etat_machine,
            "mtbf":             mtbf,
            "mttr":             mttr,
            "availability":     availability,
            "utilization_rate": utilization_rate,
            "anomaly_rate":     anomaly_rate,
            "cost_estimate":    cost_estimate,
            "total_logs":       total_logs,
            "pannes_mois":      machine.pannes_mois,
            "rendement_machine": machine.rendement_machine
        }

    except Exception as e:
        print(f"[Machine Calculator] ❌ Erreur machine {machine.machine_id} : {e}")
        return None


# ============================================================
# UPSERT daily_machine_kpi
# ============================================================
def _upsert_daily_machine_kpi(kpi, machine_id, today):
    # Utiliser no_autoflush empêche SQLA de tenter l'insertion avant le commit final
    with db.session.no_autoflush:
        existing = DailyMachineKpi.query.filter_by(
            date=today,
            machine_id=machine_id
        ).first()

        if existing:
            # UPDATE
            existing.mtbf             = kpi["mtbf"]
            existing.mttr             = kpi["mttr"]
            existing.availability     = kpi["availability"]
            existing.utilization_rate = kpi["utilization_rate"]
            existing.anomaly_rate     = kpi["anomaly_rate"]
            existing.cost_estimate    = kpi["cost_estimate"]
            existing.computed_at      = datetime.now()
        else:
            # INSERT
            nouvelle_ligne = DailyMachineKpi(
                date             = today,
                machine_id       = machine_id,
                mtbf             = kpi["mtbf"],
                mttr             = kpi["mttr"],
                availability     = kpi["availability"],
                utilization_rate = kpi["utilization_rate"],
                anomaly_rate     = kpi["anomaly_rate"],
                cost_estimate    = kpi["cost_estimate"]
            )
            db.session.add(nouvelle_ligne)

# ============================================================
# GÉNÉRATION ALERTES
# ============================================================
def _generer_alertes(kpi, machine, today):
    alertes = []

    # Disponibilité basse
    if kpi["availability"] < SEUIL_AVAILABILITY_CRIT:
        alertes.append(MachineAlert(
            date       = today,
            machine_id = machine.machine_id,
            alert_type = "LOW_AVAILABILITY",
            severity   = "critical",
            message    = f"{machine.nom_machine} — disponibilité critique : {kpi['availability']*100}%"
        ))
    elif kpi["availability"] < SEUIL_AVAILABILITY_WARN:
        alertes.append(MachineAlert(
            date       = today,
            machine_id = machine.machine_id,
            alert_type = "LOW_AVAILABILITY",
            severity   = "warning",
            message    = f"{machine.nom_machine} — disponibilité basse : {kpi['availability']*100}%"
        ))

    # Anomalies élevées
    if kpi["anomaly_rate"] > SEUIL_ANOMALY_CRIT:
        alertes.append(MachineAlert(
            date       = today,
            machine_id = machine.machine_id,
            alert_type = "HIGH_ANOMALY_RATE",
            severity   = "critical",
            message    = f"{machine.nom_machine} — taux anomalies critique : {round(kpi['anomaly_rate']*100, 1)}%"
        ))
    elif kpi["anomaly_rate"] > SEUIL_ANOMALY_WARN:
        alertes.append(MachineAlert(
            date       = today,
            machine_id = machine.machine_id,
            alert_type = "HIGH_ANOMALY_RATE",
            severity   = "warning",
            message    = f"{machine.nom_machine} — taux anomalies élevé : {round(kpi['anomaly_rate']*100, 1)}%"
        ))

    # Sous-utilisation
    if kpi["utilization_rate"] < SEUIL_UTILIZATION_WARN:
        alertes.append(MachineAlert(
            date       = today,
            machine_id = machine.machine_id,
            alert_type = "LOW_UTILIZATION",
            severity   = "warning",
            message    = f"{machine.nom_machine} — sous-utilisée : {round(kpi['utilization_rate']*100, 1)}%"
        ))

    # Machine en panne
    if machine.etat_machine != "Actif":
        alertes.append(MachineAlert(
            date       = today,
            machine_id = machine.machine_id,
            alert_type = "MACHINE_DOWN",
            severity   = "critical",
            message    = f"{machine.nom_machine} — état : {machine.etat_machine}"
        ))

    # Insert sans doublons
    for alerte in alertes:
        existe = MachineAlert.query.filter_by(
            date       = today,
            machine_id = alerte.machine_id,
            alert_type = alerte.alert_type
        ).first()
        if not existe:
            db.session.add(alerte)