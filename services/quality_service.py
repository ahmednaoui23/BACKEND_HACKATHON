from config import db
from models.machine import Machine
from models.factory_log import FactoryLog
from models.daily_quality_kpi import DailyQualityKpi
from models.quality_alert import QualityAlert
from datetime import date, timedelta
import traceback

OPPORTUNITES_PAR_UNITE = 5

def _calculer_qualite_machine_volée(machine):
    logs = FactoryLog.query.filter_by(machine_id=machine.machine_id).all()
    logs_today = [
        l for l in logs
        if l.tag_event_start and l.tag_event_start[:10] == str(date.today())
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

    if anomaly_rate < 0.05 and rejection_rate < 0.05:
        statut = "ok"
    elif anomaly_rate < 0.25 and rejection_rate < 0.15:
        statut = "warning"
    else:
        statut = "critical"

    return {
        "machine_id":          machine.machine_id,
        "nom_machine":         machine.nom_machine,
        "atelier":             machine.atelier,
        "kpi": {
            "anomaly_rate":       anomaly_rate,
            "first_pass_quality": first_pass_quality,
            "rejection_rate":     rejection_rate,
            "dpmo":               dpmo,
            "stability":          machine.rendement_machine,
            "total_taches":       total
        },
        "statut": statut
    }


def get_kpi_qualite_today():
    try:
        machines = Machine.query.all()
        if not machines:
            return {"statut": "vide", "message": "Aucune machine trouvée"}, 404
        result = [_calculer_qualite_machine_volée(m) for m in machines]
        ordre  = {"critical": 0, "warning": 1, "ok": 2}
        result.sort(key=lambda x: ordre[x["statut"]])
        return result
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_kpi_qualite_machine(machine_id):
    try:
        m = Machine.query.filter_by(machine_id=machine_id).first()
        if not m:
            return {"statut": "erreur", "message": f"Machine '{machine_id}' non trouvée"}, 404
        return _calculer_qualite_machine_volée(m)
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_kpi_qualite_atelier(atelier):
    try:
        machines = Machine.query.filter_by(atelier=atelier).all()
        if not machines:
            return {"statut": "erreur", "message": f"Aucune machine pour atelier '{atelier}'"}, 404
        result = [_calculer_qualite_machine_volée(m) for m in machines]
        ordre  = {"critical": 0, "warning": 1, "ok": 2}
        result.sort(key=lambda x: ordre[x["statut"]])
        return result
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_kpi_qualite_global():
    try:
        today = date.today()
        row   = DailyQualityKpi.query.filter_by(date=today, machine_id="ALL").first()
        if not row:
            return {"statut": "vide", "message": "Pas encore calculé pour aujourd'hui"}, 404
        return {
            "date":               row.date.isoformat(),
            "anomaly_rate":       row.anomaly_rate,
            "first_pass_quality": row.first_pass_quality,
            "rejection_rate":     row.rejection_rate,
            "dpmo":               row.dpmo,
            "stability":          row.stability,
            "computed_at":        row.computed_at.isoformat()
        }
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_kpi_qualite_series(machine_id="ALL"):
    try:
        today                = date.today()
        debut_mois_actuel    = today.replace(day=1)
        debut_mois_precedent = (debut_mois_actuel - timedelta(days=1)).replace(day=1)

        rows = DailyQualityKpi.query.filter(
            DailyQualityKpi.machine_id == machine_id,
            DailyQualityKpi.date       >= debut_mois_precedent
        ).order_by(DailyQualityKpi.date).all()

        previous_month = []
        current_month  = []

        for r in rows:
            point = {
                "date":               r.date.isoformat(),
                "anomaly_rate":       r.anomaly_rate,
                "first_pass_quality": r.first_pass_quality,
                "rejection_rate":     r.rejection_rate,
                "dpmo":               r.dpmo,
                "stability":          r.stability
            }
            if r.date < debut_mois_actuel:
                previous_month.append(point)
            else:
                current_month.append(point)

        return {
            "machine_id":     machine_id,
            "previous_month": previous_month,
            "current_month":  current_month
        }
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_quality_alerts(severity=None):
    try:
        query = QualityAlert.query.filter_by(is_read=False).order_by(QualityAlert.created_at.desc())
        if severity:
            query = query.filter_by(severity=severity)
        alerts = query.limit(50).all()
        return [
            {
                "id":         a.id,
                "date":       a.date.isoformat(),
                "machine_id": a.machine_id,
                "alert_type": a.alert_type,
                "severity":   a.severity,
                "message":    a.message,
                "created_at": a.created_at.isoformat()
            }
            for a in alerts
        ]
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def mark_quality_alert_read(alert_id):
    try:
        a = QualityAlert.query.get(alert_id)
        if not a:
            return {"statut": "erreur", "message": "Alerte non trouvée"}, 404
        a.is_read = True
        db.session.commit()
        return {"message": "Alerte marquée comme lue"}
    except Exception as e:
        db.session.rollback()
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500