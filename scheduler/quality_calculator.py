from models.machine import Machine
from models.factory_log import FactoryLog
from models.daily_quality_kpi import DailyQualityKpi
from models.quality_alert import QualityAlert
from config import db
from datetime import date, datetime

# ============================================================
# SEUILS
# ============================================================
SEUIL_ANOMALY_WARN       = 0.10
SEUIL_ANOMALY_CRIT       = 0.25
SEUIL_REJECTION_WARN     = 0.05
SEUIL_REJECTION_CRIT     = 0.15
SEUIL_FPQ_WARN           = 0.85
SEUIL_DPMO_WARN          = 10000
SEUIL_DPMO_CRIT          = 50000
OPPORTUNITES_PAR_UNITE   = 5


# ============================================================
# FONCTION PRINCIPALE
# ============================================================
def calculer_et_stocker_quality_kpi():
    today    = date.today()
    machines = Machine.query.all()

    if not machines:
        print("[Quality Scheduler] ⚠️ Aucune machine trouvée")
        return

    # Calcul global usine (machine_id = 'ALL')
    _calculer_global(today)

    # Calcul par machine
    for machine in machines:
        kpi = _calculer_kpi_qualite(machine, today)
        if kpi:
            _upsert_daily_quality_kpi(kpi, machine.machine_id, today)
            _generer_alertes(kpi, machine, today)

    db.session.commit()
    print(f"[Quality Scheduler] ✅ KPI calculés pour {today} à {datetime.now().strftime('%H:%M:%S')}")


# ============================================================
# CALCUL GLOBAL USINE
# ============================================================
def _calculer_global(today):
    # Rollback d'abord pour nettoyer la session
    try:
        db.session.rollback()
    except:
        pass

    logs_today = [
        l for l in FactoryLog.query.all()
        if l.tag_event_start and l.tag_event_start[:10] == str(today)
    ]

    total           = len(logs_today)
    total_anomalies = sum(1 for l in logs_today if l.anomaly_flag == 1)
    total_rejected  = sum(1 for l in logs_today if l.task_status == "Failed")

    anomaly_rate       = round(total_anomalies / total, 4) if total > 0 else 0.0
    first_pass_quality = round(1 - anomaly_rate, 4)
    rejection_rate     = round(total_rejected / total, 4) if total > 0 else 0.0
    dpmo               = round(
        (total_anomalies / (total * OPPORTUNITES_PAR_UNITE)) * 1_000_000, 2
    ) if total > 0 else 0.0

    machines      = Machine.query.all()
    avg_rendement = round(
        sum(m.rendement_machine for m in machines) / len(machines), 4
    ) if machines else 0.0

    # UPSERT propre avec merge
    existing = DailyQualityKpi.query.filter_by(
        date=today, machine_id="ALL"
    ).first()

    if existing:
        existing.anomaly_rate       = anomaly_rate
        existing.first_pass_quality = first_pass_quality
        existing.rejection_rate     = rejection_rate
        existing.dpmo               = dpmo
        existing.stability          = avg_rendement
        existing.computed_at        = datetime.now()
    else:
        nouvelle = DailyQualityKpi(
            date               = today,
            machine_id         = "ALL",
            anomaly_rate       = anomaly_rate,
            first_pass_quality = first_pass_quality,
            rejection_rate     = rejection_rate,
            dpmo               = dpmo,
            stability          = avg_rendement
        )
        db.session.add(nouvelle)

    # Commit immédiat pour éviter conflit avec la boucle machines
    db.session.commit()

# ============================================================
# CALCUL PAR MACHINE
# ============================================================
def _calculer_kpi_qualite(machine, today):
    try:
        logs = FactoryLog.query.filter_by(machine_id=machine.machine_id).all()
        logs_today = [
            l for l in logs
            if l.tag_event_start and l.tag_event_start[:10] == str(today)
        ]

        total           = len(logs_today)
        total_anomalies = sum(1 for l in logs_today if l.anomaly_flag == 1)
        total_rejected  = sum(1 for l in logs_today if l.task_status == "Failed")

        anomaly_rate       = round(total_anomalies / total, 4) if total > 0 else 0.0
        first_pass_quality = round(1 - anomaly_rate, 4)
        rejection_rate     = round(total_rejected / total, 4) if total > 0 else 0.0
        dpmo               = round(
            (total_anomalies / (total * OPPORTUNITES_PAR_UNITE)) * 1_000_000, 2
        ) if total > 0 else 0.0
        stability          = machine.rendement_machine

        return {
            "machine_id":        machine.machine_id,
            "nom_machine":       machine.nom_machine,
            "atelier":           machine.atelier,
            "anomaly_rate":      anomaly_rate,
            "first_pass_quality": first_pass_quality,
            "rejection_rate":    rejection_rate,
            "dpmo":              dpmo,
            "stability":         stability,
            "total":             total
        }
    except Exception as e:
        print(f"[Quality Calculator] ❌ Erreur machine {machine.machine_id} : {e}")
        return None


# ============================================================
# UPSERT
# ============================================================
def _upsert_daily_quality_kpi(kpi, machine_id, today):
    existing = DailyQualityKpi.query.filter_by(date=today, machine_id=machine_id).first()
    if existing:
        existing.anomaly_rate       = kpi["anomaly_rate"]
        existing.first_pass_quality = kpi["first_pass_quality"]
        existing.rejection_rate     = kpi["rejection_rate"]
        existing.dpmo               = kpi["dpmo"]
        existing.stability          = kpi["stability"]
        existing.computed_at        = datetime.now()
    else:
        db.session.add(DailyQualityKpi(
            date               = today,
            machine_id         = machine_id,
            anomaly_rate       = kpi["anomaly_rate"],
            first_pass_quality = kpi["first_pass_quality"],
            rejection_rate     = kpi["rejection_rate"],
            dpmo               = kpi["dpmo"],
            stability          = kpi["stability"]
        ))


# ============================================================
# ALERTES
# ============================================================
def _generer_alertes(kpi, machine, today):
    alertes = []

    if kpi["anomaly_rate"] > SEUIL_ANOMALY_CRIT:
        alertes.append(QualityAlert(
            date       = today,
            machine_id = machine.machine_id,
            alert_type = "HIGH_ANOMALY_RATE",
            severity   = "critical",
            message    = f"{machine.nom_machine} — anomalies critiques : {round(kpi['anomaly_rate']*100,1)}%"
        ))
    elif kpi["anomaly_rate"] > SEUIL_ANOMALY_WARN:
        alertes.append(QualityAlert(
            date       = today,
            machine_id = machine.machine_id,
            alert_type = "HIGH_ANOMALY_RATE",
            severity   = "warning",
            message    = f"{machine.nom_machine} — anomalies élevées : {round(kpi['anomaly_rate']*100,1)}%"
        ))

    if kpi["rejection_rate"] > SEUIL_REJECTION_CRIT:
        alertes.append(QualityAlert(
            date       = today,
            machine_id = machine.machine_id,
            alert_type = "HIGH_REJECTION_RATE",
            severity   = "critical",
            message    = f"{machine.nom_machine} — rejet critique : {round(kpi['rejection_rate']*100,1)}%"
        ))
    elif kpi["rejection_rate"] > SEUIL_REJECTION_WARN:
        alertes.append(QualityAlert(
            date       = today,
            machine_id = machine.machine_id,
            alert_type = "HIGH_REJECTION_RATE",
            severity   = "warning",
            message    = f"{machine.nom_machine} — rejet élevé : {round(kpi['rejection_rate']*100,1)}%"
        ))

    if kpi["first_pass_quality"] < SEUIL_FPQ_WARN:
        alertes.append(QualityAlert(
            date       = today,
            machine_id = machine.machine_id,
            alert_type = "LOW_FIRST_PASS_QUALITY",
            severity   = "warning",
            message    = f"{machine.nom_machine} — FPQ basse : {round(kpi['first_pass_quality']*100,1)}%"
        ))

    if kpi["dpmo"] > SEUIL_DPMO_CRIT:
        alertes.append(QualityAlert(
            date       = today,
            machine_id = machine.machine_id,
            alert_type = "HIGH_DPMO",
            severity   = "critical",
            message    = f"{machine.nom_machine} — DPMO critique : {kpi['dpmo']}"
        ))
    elif kpi["dpmo"] > SEUIL_DPMO_WARN:
        alertes.append(QualityAlert(
            date       = today,
            machine_id = machine.machine_id,
            alert_type = "HIGH_DPMO",
            severity   = "warning",
            message    = f"{machine.nom_machine} — DPMO élevé : {kpi['dpmo']}"
        ))

    for alerte in alertes:
        existe = QualityAlert.query.filter_by(
            date       = today,
            machine_id = alerte.machine_id,
            alert_type = alerte.alert_type
        ).first()
        if not existe:
            db.session.add(alerte)