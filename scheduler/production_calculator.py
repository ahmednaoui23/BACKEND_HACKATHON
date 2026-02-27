from models.machine import Machine
from models.factory_log import FactoryLog
from models.daily_production_kpi import DailyProductionKpi
from models.production_alert import ProductionAlert
from config import db
from datetime import date, datetime
import statistics

# ============================================================
# SEUILS
# ============================================================
SEUIL_YIELD_WARN        = 0.70
SEUIL_YIELD_CRIT        = 0.55
SEUIL_OEE_WARN          = 0.65
SEUIL_OEE_CRIT          = 0.50
SEUIL_INTERRUPTION_WARN = 0.15
SEUIL_INTERRUPTION_CRIT = 0.30
SEUIL_COMPLETION_WARN   = 0.70


# ============================================================
# FONCTION PRINCIPALE
# ============================================================
def calculer_et_stocker_production_kpi():
    today = date.today()

    # Récupérer tous les ateliers distincts
    ateliers = [a[0] for a in db.session.query(Machine.atelier).distinct().all()]

    shifts = ["Matin", "Après-midi", "Nuit", "ALL"]

    # Calcul global usine (atelier=ALL, shift=ALL)
    for shift in shifts:
        kpi = _calculer_kpi_production(shift, "ALL", today)
        if kpi:
            _upsert_daily_production_kpi(kpi, shift, "ALL", today)
            _generer_alertes(kpi, shift, "ALL", today)

    # Calcul par atelier
    for atelier in ateliers:
        for shift in shifts:
            kpi = _calculer_kpi_production(shift, atelier, today)
            if kpi:
                _upsert_daily_production_kpi(kpi, shift, atelier, today)
                _generer_alertes(kpi, shift, atelier, today)

    db.session.commit()
    print(f"[Production Scheduler] ✅ KPI calculés pour {today} à {datetime.now().strftime('%H:%M:%S')}")


# ============================================================
# CALCUL KPI PRODUCTION
# ============================================================
def _calculer_kpi_production(shift, atelier, today):
    try:
        # Récupérer les machines selon atelier
        if atelier == "ALL":
            machines = Machine.query.all()
        else:
            machines = Machine.query.filter_by(atelier=atelier).all()

        if not machines:
            return None

        machine_ids = [m.machine_id for m in machines]

        # Récupérer les logs du jour
        tous_logs = FactoryLog.query.filter(
            FactoryLog.machine_id.in_(machine_ids)
        ).all()

        logs_today = tous_logs

        # Filtrer par shift si nécessaire
        if shift != "ALL":
            logs_today = [l for l in logs_today if l.shift == shift]

        if not logs_today:
            return None

        total = len(logs_today)

        # --- Taux Completion ---
        taux_completion = round(
            sum(1 for l in logs_today if l.task_status == "completed") / total, 4
        )

        # --- Interruption Rate ---
        interruption_rate = round(
            sum(1 for l in logs_today if l.task_status == "Interrupted") / total, 4
        )

        # --- Efficiency (durée réelle vs théorique) ---
        durees = [l.task_duration_min for l in logs_today if l.task_duration_min and l.task_duration_min > 0]
        avg_duration = sum(durees) / len(durees) if durees else 0

        avg_theorique = sum(m.temps_par_unite_min for m in machines) / len(machines) if machines else 1
        efficiency = round(avg_theorique / avg_duration, 4) if avg_duration > 0 else 0
        efficiency = min(efficiency, 1.0)

        # --- Stability (1 - coefficient de variation) ---
        if len(durees) > 1:
            cv = statistics.stdev(durees) / avg_duration if avg_duration > 0 else 0
            stability = round(max(1 - cv, 0), 4)
        else:
            stability = 1.0

        # --- Global Yield ---
        global_yield = round(
            taux_completion * 0.40 +
            efficiency * 0.35 +
            stability * 0.25, 4
        )

        # --- OEE ---
        disponibilite = round(
            sum(1 for m in machines if m.etat_machine == "Opérationnelle") / len(machines), 4
        )
        qualite = round(
            sum(1 for l in logs_today if l.anomaly_flag == 0) / total, 4
        )
        oee = round(disponibilite * efficiency * qualite, 4)

        # --- Duration Ratio ---
        duration_ratio = round(avg_duration / avg_theorique, 4) if avg_theorique > 0 else 1.0

        # --- Cadence (tâches par heure) ---
        starts = [l.tag_event_start for l in logs_today if l.tag_event_start]
        ends   = [l.tag_event_end for l in logs_today if l.tag_event_end]

        if starts and ends:
            try:
                from datetime import datetime as dt
                min_start = min(dt.fromisoformat(s) for s in starts)
                max_end   = max(dt.fromisoformat(e) for e in ends)
                heures    = (max_end - min_start).total_seconds() / 3600
                cadence   = round(total / heures, 2) if heures > 0 else 0
            except:
                cadence = 0
        else:
            cadence = 0

        return {
            "shift":            shift,
            "atelier":          atelier,
            "taux_completion":  taux_completion,
            "efficiency":       efficiency,
            "stability":        stability,
            "global_yield":     global_yield,
            "oee":              oee,
            "duration_ratio":   duration_ratio,
            "cadence":          cadence,
            "interruption_rate": interruption_rate,
            "total":            total
        }

    except Exception as e:
        print(f"[Production Calculator] ❌ Erreur shift={shift} atelier={atelier} : {e}")
        return None


# ============================================================
# UPSERT daily_production_kpi
# ============================================================
def _upsert_daily_production_kpi(kpi, shift, atelier, today):
    existing = DailyProductionKpi.query.filter_by(
        date=today, shift=shift, atelier=atelier
    ).first()

    if existing:
        existing.taux_completion   = kpi["taux_completion"]
        existing.efficiency        = kpi["efficiency"]
        existing.stability         = kpi["stability"]
        existing.global_yield      = kpi["global_yield"]
        existing.oee               = kpi["oee"]
        existing.duration_ratio    = kpi["duration_ratio"]
        existing.cadence           = kpi["cadence"]
        existing.interruption_rate = kpi["interruption_rate"]
        existing.computed_at       = datetime.now()
    else:
        db.session.add(DailyProductionKpi(
            date              = today,
            shift             = shift,
            atelier           = atelier,
            taux_completion   = kpi["taux_completion"],
            efficiency        = kpi["efficiency"],
            stability         = kpi["stability"],
            global_yield      = kpi["global_yield"],
            oee               = kpi["oee"],
            duration_ratio    = kpi["duration_ratio"],
            cadence           = kpi["cadence"],
            interruption_rate = kpi["interruption_rate"]
        ))


# ============================================================
# GÉNÉRATION ALERTES
# ============================================================
def _generer_alertes(kpi, shift, atelier, today):
    alertes = []

    # Global Yield bas
    if kpi["global_yield"] < SEUIL_YIELD_CRIT:
        alertes.append(ProductionAlert(
            date       = today,
            shift      = shift,
            atelier    = atelier,
            alert_type = "LOW_GLOBAL_YIELD",
            severity   = "critical",
            message    = f"Rendement critique {atelier}/{shift} : {round(kpi['global_yield']*100,1)}%"
        ))
    elif kpi["global_yield"] < SEUIL_YIELD_WARN:
        alertes.append(ProductionAlert(
            date       = today,
            shift      = shift,
            atelier    = atelier,
            alert_type = "LOW_GLOBAL_YIELD",
            severity   = "warning",
            message    = f"Rendement bas {atelier}/{shift} : {round(kpi['global_yield']*100,1)}%"
        ))

    # OEE bas
    if kpi["oee"] < SEUIL_OEE_CRIT:
        alertes.append(ProductionAlert(
            date       = today,
            shift      = shift,
            atelier    = atelier,
            alert_type = "LOW_OEE",
            severity   = "critical",
            message    = f"OEE critique {atelier}/{shift} : {round(kpi['oee']*100,1)}%"
        ))
    elif kpi["oee"] < SEUIL_OEE_WARN:
        alertes.append(ProductionAlert(
            date       = today,
            shift      = shift,
            atelier    = atelier,
            alert_type = "LOW_OEE",
            severity   = "warning",
            message    = f"OEE bas {atelier}/{shift} : {round(kpi['oee']*100,1)}%"
        ))

    # Interruptions élevées
    if kpi["interruption_rate"] > SEUIL_INTERRUPTION_CRIT:
        alertes.append(ProductionAlert(
            date       = today,
            shift      = shift,
            atelier    = atelier,
            alert_type = "HIGH_INTERRUPTION",
            severity   = "critical",
            message    = f"Interruptions critiques {atelier}/{shift} : {round(kpi['interruption_rate']*100,1)}%"
        ))
    elif kpi["interruption_rate"] > SEUIL_INTERRUPTION_WARN:
        alertes.append(ProductionAlert(
            date       = today,
            shift      = shift,
            atelier    = atelier,
            alert_type = "HIGH_INTERRUPTION",
            severity   = "warning",
            message    = f"Interruptions élevées {atelier}/{shift} : {round(kpi['interruption_rate']*100,1)}%"
        ))

    # Completion basse
    if kpi["taux_completion"] < SEUIL_COMPLETION_WARN:
        alertes.append(ProductionAlert(
            date       = today,
            shift      = shift,
            atelier    = atelier,
            alert_type = "LOW_COMPLETION",
            severity   = "warning",
            message    = f"Complétion basse {atelier}/{shift} : {round(kpi['taux_completion']*100,1)}%"
        ))

    # Insert sans doublons
    for alerte in alertes:
        existe = ProductionAlert.query.filter_by(
            date       = today,
            shift      = alerte.shift,
            atelier    = alerte.atelier,
            alert_type = alerte.alert_type
        ).first()
        if not existe:
            db.session.add(alerte)