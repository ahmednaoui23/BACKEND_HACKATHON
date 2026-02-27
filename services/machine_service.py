from config import db
from models.machine import Machine
from models.factory_log import FactoryLog
from models.daily_machine_kpi import DailyMachineKpi
from models.machine_alert import MachineAlert
from datetime import date, timedelta
import traceback


# ============================================================
# FONCTION UTILITAIRE INTERNE
# ============================================================
def _calculer_kpi_machine_volée(machine):
    """Calcule les KPI d'une machine à la volée"""

    logs = FactoryLog.query.filter_by(machine_id=machine.machine_id).all()
    logs_today = [
        l for l in logs
        if l.tag_event_start and l.tag_event_start[:10] == str(date.today())
    ]

    total_logs      = len(logs_today)
    total_anomalies = sum(1 for l in logs_today if l.anomaly_flag == 1)
    anomaly_rate    = round(total_anomalies / total_logs, 4) if total_logs > 0 else 0.0
    availability    = 1.0 if machine.etat_machine == "Opérationnelle" else 0.0
    utilization_rate = round(
        min(total_logs / machine.capacite, 1.0), 4
    ) if machine.capacite > 0 else 0.0

    heures_mois   = 160.0
    mtbf          = round(heures_mois / machine.pannes_mois, 2) if machine.pannes_mois > 0 else heures_mois
    mttr          = round(mtbf * 0.10, 2)
    cost_estimate = round(machine.pannes_mois * 150.0, 2)

    if availability == 1.0 and anomaly_rate < 0.10:
        statut = "ok"
    elif availability == 1.0 and anomaly_rate < 0.25:
        statut = "warning"
    else:
        statut = "critical"

    return {
        "machine_id":        machine.machine_id,
        "nom_machine":       machine.nom_machine,
        "type_machine":      machine.type_machine,
        "atelier":           machine.atelier,
        "etat_machine":      machine.etat_machine,
        "rendement_machine": machine.rendement_machine,
        "kpi": {
            "mtbf":             mtbf,
            "mttr":             mttr,
            "availability":     availability,
            "utilization_rate": utilization_rate,
            "anomaly_rate":     anomaly_rate,
            "cost_estimate":    cost_estimate,
            "total_taches":     total_logs
        },
        "statut": statut
    }


# ============================================================
# CRUD EXISTANT
# ============================================================
def get_all_machines(atelier=None, type_machine=None, etat=None):
    try:
        query = Machine.query
        if atelier:
            query = query.filter_by(atelier=atelier)
        if type_machine:
            query = query.filter_by(type_machine=type_machine)
        if etat:
            query = query.filter_by(etat_machine=etat)
        machines = query.all()
        if not machines:
            return {"statut": "erreur", "message": "Aucune machine trouvée"}, 404
        return [
            {
                "machine_id":        m.machine_id,
                "nom_machine":       m.nom_machine,
                "type_machine":      m.type_machine,
                "atelier":           m.atelier,
                "tache":             m.tache,
                "capacite":          m.capacite,
                "etat_machine":      m.etat_machine,
                "pannes_mois":       m.pannes_mois,
                "rendement_machine": m.rendement_machine,
                "annee_installation": m.annee_installation,
                "marque":            m.marque
            }
            for m in machines
        ]
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_machine_by_id(machine_id):
    try:
        m = Machine.query.filter_by(machine_id=machine_id).first()
        if not m:
            return {"statut": "erreur", "message": f"Machine '{machine_id}' non trouvée"}, 404
        return {
            "machine_id":          m.machine_id,
            "nom_machine":         m.nom_machine,
            "type_machine":        m.type_machine,
            "atelier":             m.atelier,
            "tache":               m.tache,
            "unite_production":    m.unite_production,
            "capacite":            m.capacite,
            "temps_par_unite_min": m.temps_par_unite_min,
            "temps_total_tache_min": m.temps_total_tache_min,
            "operateurs_requis":   m.operateurs_requis,
            "pannes_mois":         m.pannes_mois,
            "etat_machine":        m.etat_machine,
            "annee_installation":  m.annee_installation,
            "marque":              m.marque,
            "consommation_energie": m.consommation_energie,
            "rendement_machine":   m.rendement_machine
        }
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def create_machine(data):
    try:
        m = Machine(**data)
        db.session.add(m)
        db.session.commit()
        return {"message": "Machine créée avec succès", "machine_id": m.machine_id}
    except Exception as e:
        db.session.rollback()
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def update_machine(machine_id, data):
    try:
        m = Machine.query.filter_by(machine_id=machine_id).first()
        if not m:
            return {"statut": "erreur", "message": f"Machine '{machine_id}' non trouvée"}, 404
        for key, value in data.items():
            setattr(m, key, value)
        db.session.commit()
        return {"message": "Machine mise à jour avec succès"}
    except Exception as e:
        db.session.rollback()
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def delete_machine(machine_id):
    try:
        m = Machine.query.filter_by(machine_id=machine_id).first()
        if not m:
            return {"statut": "erreur", "message": f"Machine '{machine_id}' non trouvée"}, 404
        db.session.delete(m)
        db.session.commit()
        return {"message": "Machine supprimée avec succès"}
    except Exception as e:
        db.session.rollback()
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


# ============================================================
# KPI NOUVEAUX
# ============================================================
def get_kpi_machines_today():
    """Toutes les machines + KPI"""
    try:
        machines = Machine.query.all()
        if not machines:
            return {"statut": "vide", "message": "Aucune machine trouvée"}, 404

        result = [_calculer_kpi_machine_volée(m) for m in machines]

        ordre = {"critical": 0, "warning": 1, "ok": 2}
        result.sort(key=lambda x: ordre[x["statut"]])
        return result
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_kpi_machine_by_id(machine_id):
    """1 machine précise par ID"""
    try:
        m = Machine.query.filter_by(machine_id=machine_id).first()
        if not m:
            return {"statut": "erreur", "message": f"Machine '{machine_id}' non trouvée"}, 404
        return _calculer_kpi_machine_volée(m)
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_kpi_by_atelier(atelier):
    """Toutes les machines d'un atelier"""
    try:
        machines = Machine.query.filter_by(atelier=atelier).all()
        if not machines:
            return {"statut": "erreur", "message": f"Aucune machine trouvée pour l'atelier '{atelier}'"}, 404

        result = [_calculer_kpi_machine_volée(m) for m in machines]

        ordre = {"critical": 0, "warning": 1, "ok": 2}
        result.sort(key=lambda x: ordre[x["statut"]])
        return result
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_kpi_machines_aggregated():
    """KPI agrégé depuis daily_machine_kpi"""
    try:
        today = date.today()
        rows  = DailyMachineKpi.query.filter_by(date=today).all()
        if not rows:
            return {"statut": "vide", "message": "Pas encore calculé pour aujourd'hui"}, 404
        return [
            {
                "machine_id":       r.machine_id,
                "mtbf":             r.mtbf,
                "mttr":             r.mttr,
                "availability":     r.availability,
                "utilization_rate": r.utilization_rate,
                "anomaly_rate":     r.anomaly_rate,
                "cost_estimate":    r.cost_estimate,
                "computed_at":      r.computed_at.isoformat()
            }
            for r in rows
        ]
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_kpi_machine_series(machine_id):
    """Séries temporelles mois précédent vs mois actuel pour 1 machine"""
    try:
        today                = date.today()
        debut_mois_actuel    = today.replace(day=1)
        debut_mois_precedent = (debut_mois_actuel - timedelta(days=1)).replace(day=1)

        rows = DailyMachineKpi.query.filter(
            DailyMachineKpi.machine_id == machine_id,
            DailyMachineKpi.date       >= debut_mois_precedent
        ).order_by(DailyMachineKpi.date).all()

        previous_month = []
        current_month  = []

        for r in rows:
            point = {
                "date":             r.date.isoformat(),
                "mtbf":             r.mtbf,
                "availability":     r.availability,
                "utilization_rate": r.utilization_rate,
                "anomaly_rate":     r.anomaly_rate,
                "cost_estimate":    r.cost_estimate
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


def get_machine_alerts(severity=None):
    """Alertes machines actives non lues"""
    try:
        query = MachineAlert.query.filter_by(is_read=False).order_by(MachineAlert.created_at.desc())
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


def mark_machine_alert_read(alert_id):
    """Marquer une alerte machine comme lue"""
    try:
        a = MachineAlert.query.get(alert_id)
        if not a:
            return {"statut": "erreur", "message": "Alerte non trouvée"}, 404
        a.is_read = True
        db.session.commit()
        return {"message": "Alerte marquée comme lue"}
    except Exception as e:
        db.session.rollback()
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500