from config import db
from models.machine import Machine
from models.factory_log import FactoryLog
from models.daily_production_kpi import DailyProductionKpi
from models.production_alert import ProductionAlert
from datetime import date, timedelta
import statistics
import traceback


def _calculer_production_volée(shift, atelier, today=None):
    if today is None:
        today = date.today()

    if atelier == "ALL":
        machines = Machine.query.all()
    else:
        machines = Machine.query.filter_by(atelier=atelier).all()

    if not machines:
        return None

    machine_ids = [m.machine_id for m in machines]
    tous_logs   = FactoryLog.query.filter(FactoryLog.machine_id.in_(machine_ids)).all()
    logs_today  = [
        l for l in tous_logs
        if l.tag_event_start and l.tag_event_start[:10] == str(today)
    ]

    if shift != "ALL":
        logs_today = [l for l in logs_today if l.shift == shift]

    if not logs_today:
        return None

    total             = len(logs_today)
    taux_completion   = round(sum(1 for l in logs_today if l.task_status == "completed") / total, 4)
    interruption_rate = round(sum(1 for l in logs_today if l.task_status == "Interrupted") / total, 4)

    durees       = [l.task_duration_min for l in logs_today if l.task_duration_min and l.task_duration_min > 0]
    avg_duration = sum(durees) / len(durees) if durees else 0
    avg_theorique = sum(m.temps_par_unite_min for m in machines) / len(machines) if machines else 1

    efficiency = round(min(avg_theorique / avg_duration, 1.0), 4) if avg_duration > 0 else 0
    stability  = round(max(1 - (statistics.stdev(durees) / avg_duration if avg_duration > 0 else 0), 0), 4) if len(durees) > 1 else 1.0

    global_yield  = round(taux_completion * 0.40 + efficiency * 0.35 + stability * 0.25, 4)
    disponibilite = round(sum(1 for m in machines if m.etat_machine == "Opérationnelle") / len(machines), 4)
    qualite       = round(sum(1 for l in logs_today if l.anomaly_flag == 0) / total, 4)
    oee           = round(disponibilite * efficiency * qualite, 4)
    duration_ratio = round(avg_duration / avg_theorique, 4) if avg_theorique > 0 else 1.0

    if global_yield >= 0.80 and oee >= 0.65:
        statut = "ok"
    elif global_yield >= 0.55 and oee >= 0.50:
        statut = "warning"
    else:
        statut = "critical"

    return {
        "shift":            shift,
        "atelier":          atelier,
        "taux_completion":  taux_completion,
        "efficiency":       efficiency,
        "stability":        stability,
        "global_yield":     global_yield,
        "oee":              oee,
        "duration_ratio":   duration_ratio,
        "interruption_rate": interruption_rate,
        "total_taches":     total,
        "statut":           statut
    }


def get_kpi_production_today():
    """KPI global usine tous shifts"""
    try:
        today   = date.today()
        shifts  = ["Matin", "Après-midi", "Nuit", "ALL"]
        result  = []
        for shift in shifts:
            kpi = _calculer_production_volée(shift, "ALL", today)
            if kpi:
                result.append(kpi)
        return result
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_kpi_production_by_shift(shift):
    """KPI par shift — tous ateliers"""
    try:
        today    = date.today()
        ateliers = [a[0] for a in db.session.query(Machine.atelier).distinct().all()]
        result   = []
        for atelier in ateliers:
            kpi = _calculer_production_volée(shift, atelier, today)
            if kpi:
                result.append(kpi)
        ordre = {"critical": 0, "warning": 1, "ok": 2}
        result.sort(key=lambda x: ordre[x["statut"]])
        return result
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_kpi_production_by_atelier(atelier):
    """KPI par atelier — tous shifts"""
    try:
        today  = date.today()
        shifts = ["Matin", "Après-midi", "Nuit", "ALL"]
        result = []
        for shift in shifts:
            kpi = _calculer_production_volée(shift, atelier, today)
            if kpi:
                result.append(kpi)
        return result
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_kpi_production_aggregated():
    """KPI agrégés depuis daily_production_kpi"""
    try:
        today = date.today()
        rows  = DailyProductionKpi.query.filter_by(date=today).all()
        if not rows:
            return {"statut": "vide", "message": "Pas encore calculé pour aujourd'hui"}, 404
        return [
            {
                "shift":            r.shift,
                "atelier":          r.atelier,
                "taux_completion":  r.taux_completion,
                "efficiency":       r.efficiency,
                "stability":        r.stability,
                "global_yield":     r.global_yield,
                "oee":              r.oee,
                "duration_ratio":   r.duration_ratio,
                "cadence":          r.cadence,
                "interruption_rate": r.interruption_rate,
                "computed_at":      r.computed_at.isoformat()
            }
            for r in rows
        ]
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_kpi_production_series(shift="ALL", atelier="ALL"):
    """Séries temporelles mois précédent vs mois actuel"""
    try:
        today                = date.today()
        debut_mois_actuel    = today.replace(day=1)
        debut_mois_precedent = (debut_mois_actuel - timedelta(days=1)).replace(day=1)

        rows = DailyProductionKpi.query.filter(
            DailyProductionKpi.shift   == shift,
            DailyProductionKpi.atelier == atelier,
            DailyProductionKpi.date    >= debut_mois_precedent
        ).order_by(DailyProductionKpi.date).all()

        previous_month = []
        current_month  = []

        for r in rows:
            point = {
                "date":             r.date.isoformat(),
                "global_yield":     r.global_yield,
                "oee":              r.oee,
                "taux_completion":  r.taux_completion,
                "efficiency":       r.efficiency,
                "interruption_rate": r.interruption_rate
            }
            if r.date < debut_mois_actuel:
                previous_month.append(point)
            else:
                current_month.append(point)

        return {
            "shift":          shift,
            "atelier":        atelier,
            "previous_month": previous_month,
            "current_month":  current_month
        }
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_production_alerts(severity=None):
    """Alertes production actives non lues"""
    try:
        query = ProductionAlert.query.filter_by(is_read=False).order_by(ProductionAlert.created_at.desc())
        if severity:
            query = query.filter_by(severity=severity)
        alerts = query.limit(50).all()
        return [
            {
                "id":         a.id,
                "date":       a.date.isoformat(),
                "shift":      a.shift,
                "atelier":    a.atelier,
                "alert_type": a.alert_type,
                "severity":   a.severity,
                "message":    a.message,
                "created_at": a.created_at.isoformat()
            }
            for a in alerts
        ]
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def mark_production_alert_read(alert_id):
    try:
        a = ProductionAlert.query.get(alert_id)
        if not a:
            return {"statut": "erreur", "message": "Alerte non trouvée"}, 404
        a.is_read = True
        db.session.commit()
        return {"message": "Alerte marquée comme lue"}
    except Exception as e:
        db.session.rollback()
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500