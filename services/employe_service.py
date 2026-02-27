from config import db
from models.employee import Employee
from models.factory_log import FactoryLog
from models.daily_hr_kpi import DailyHrKpi
from models.hr_alert import HrAlert
from datetime import date, timedelta
import traceback

# ============================================================
# CRUD EXISTANT — inchangé
# ============================================================

def get_employe_by_id(employee_id):
    try:
        e = Employee.query.filter_by(employee_id=employee_id).first()
        if not e:
            return {"statut": "erreur", "message": f"Employé '{employee_id}' non trouvé"}, 404
        return {
            "employee_id": e.employee_id,
            "nom": e.nom,
            "prenom": e.prenom,
            "sexe": e.sexe,
            "date_naissance": e.date_naissance,
            "age": e.age,
            "etat_civil": e.etat_civil,
            "nombre_enfants": e.nombre_enfants,
            "niveau_etude": e.niveau_etude,
            "poste": e.poste,
            "departement": e.departement,
            "type_contrat": e.type_contrat,
            "anciennete_annees": e.anciennete_annees,
            "salaire_mensuel": e.salaire_mensuel,
            "prime_rendement": e.prime_rendement,
            "heures_travail_semaine": e.heures_travail_semaine,
            "heures_absence_mois": e.heures_absence_mois,
            "retards_mois": e.retards_mois,
            "jours_conge_restant": e.jours_conge_restant,
            "statut_presence": e.statut_presence,
            "shift_travail": e.shift_travail,
            "performance_moyenne": e.performance_moyenne,
            "taux_rendement": e.taux_rendement,
            "accidents_travail": e.accidents_travail,
            "maladies_professionnelles": e.maladies_professionnelles,
            "evaluation_manager": e.evaluation_manager,
            "risque_absenteisme": e.risque_absenteisme,
            "risque_depart": e.risque_depart,
            "date_embauche": e.date_embauche
        }
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_all_employes(departement=None, shift=None, poste=None):
    try:
        query = Employee.query
        if departement:
            query = query.filter_by(departement=departement)
        if shift:
            query = query.filter_by(shift_travail=shift)
        if poste:
            query = query.filter_by(poste=poste)
        employes = query.all()
        if not employes:
            return {"statut": "erreur", "message": "Aucun employé trouvé"}, 404
        return [
            {
                "employee_id": e.employee_id,
                "nom": e.nom,
                "prenom": e.prenom,
                "sexe": e.sexe,
                "age": e.age,
                "poste": e.poste,
                "departement": e.departement,
                "type_contrat": e.type_contrat,
                "anciennete_annees": e.anciennete_annees,
                "salaire_mensuel": e.salaire_mensuel,
                "shift_travail": e.shift_travail,
                "statut_presence": e.statut_presence,
                "performance_moyenne": e.performance_moyenne,
                "taux_rendement": e.taux_rendement,
                "risque_absenteisme": e.risque_absenteisme,
                "risque_depart": e.risque_depart
            }
            for e in employes
        ]
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def create_employe(data):
    try:
        e = Employee(**data)
        db.session.add(e)
        db.session.commit()
        return {"message": "Employé créé avec succès", "employee_id": e.employee_id}
    except Exception as e:
        db.session.rollback()
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def update_employe(employee_id, data):
    try:
        e = Employee.query.filter_by(employee_id=employee_id).first()
        if not e:
            return {"statut": "erreur", "message": f"Employé '{employee_id}' non trouvé"}, 404
        for key, value in data.items():
            setattr(e, key, value)
        db.session.commit()
        return {"message": "Employé mis à jour avec succès"}
    except Exception as e:
        db.session.rollback()
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def delete_employe(employee_id):
    try:
        e = Employee.query.filter_by(employee_id=employee_id).first()
        if not e:
            return {"statut": "erreur", "message": f"Employé '{employee_id}' non trouvé"}, 404
        db.session.delete(e)
        db.session.commit()
        return {"message": "Employé supprimé avec succès"}
    except Exception as e:
        db.session.rollback()
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_rendement_employe(employee_id):
    try:
        e = Employee.query.filter_by(employee_id=employee_id).first()
        if not e:
            return {"statut": "erreur", "message": f"Employé '{employee_id}' non trouvé"}, 404

        taux_presence = round(
            (e.heures_travail_semaine * 4 - e.heures_absence_mois) / (e.heures_travail_semaine * 4) * 100, 2
        )
        taux_ponctualite = round((22 - e.retards_mois) / 22 * 100, 2)
        score_rendement_global = round(
            e.taux_rendement * 0.40 +
            e.performance_moyenne * 0.35 +
            e.evaluation_manager * 0.15 +
            taux_ponctualite * 0.10, 2
        )

        logs = FactoryLog.query.filter_by(employee_id=employee_id).all()
        total_taches = len(logs)
        taches_completees = sum(1 for l in logs if l.task_status == "completed")
        taux_anomalies = round(sum(1 for l in logs if l.anomaly_flag == 1) / total_taches * 100, 2) if total_taches > 0 else 0

        employes_atelier = Employee.query.filter_by(departement=e.departement).all()
        scores = []
        for emp in employes_atelier:
            tp = (emp.heures_travail_semaine * 4 - emp.heures_absence_mois) / (emp.heures_travail_semaine * 4) * 100
            sc = emp.taux_rendement * 0.40 + emp.performance_moyenne * 0.35 + emp.evaluation_manager * 0.15 + tp * 0.10
            scores.append((emp.employee_id, sc))
        scores.sort(key=lambda x: x[1], reverse=True)
        classement = next((i + 1 for i, s in enumerate(scores) if s[0] == employee_id), None)

        shift_stats = {}
        for l in logs:
            if l.task_status == "completed":
                shift_stats[l.shift] = shift_stats.get(l.shift, 0) + 1
        meilleur_shift = max(shift_stats, key=shift_stats.get) if shift_stats else None

        indice_burnout = round(
            (e.retards_mois + e.heures_absence_mois / 8 + e.accidents_travail * 5 + e.maladies_professionnelles * 3)
            / max(e.anciennete_annees, 1), 2
        )
        rendement_nocturne_ajuste = round(e.taux_rendement * 1.25, 2) if e.shift_travail == "nuit" else e.taux_rendement

        return {
            "info": {
                "employee_id": e.employee_id,
                "nom": e.nom,
                "prenom": e.prenom,
                "poste": e.poste,
                "departement": e.departement,
                "shift": e.shift_travail,
                "anciennete": e.anciennete_annees,
                "type_contrat": e.type_contrat
            },
            "normal": {
                "taux_presence": taux_presence,
                "taux_ponctualite": taux_ponctualite,
                "score_rendement_global": score_rendement_global,
                "taches_completees_mois": taches_completees,
                "taux_anomalies": taux_anomalies,
                "classement_atelier": f"{classement} / {len(scores)}",
                "meilleur_shift": meilleur_shift
            },
            "cache": {
                "indice_burnout": indice_burnout,
                "rendement_nocturne_ajuste": rendement_nocturne_ajuste,
                "risque_absenteisme": e.risque_absenteisme,
                "risque_depart": e.risque_depart
            }
        }
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_historique_employe(employee_id):
    try:
        e = Employee.query.filter_by(employee_id=employee_id).first()
        if not e:
            return {"statut": "erreur", "message": f"Employé '{employee_id}' non trouvé"}, 404
        return {
            "employee_id": employee_id,
            "performance_moyenne": e.performance_moyenne,
            "taux_rendement": e.taux_rendement,
            "evaluation_manager": e.evaluation_manager,
            "note": "Connecter à un historique mensuel pour courbe évolution"
        }
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


# ============================================================
# KPI BLOC RH — NOUVEAUX
# ============================================================

def _calculer_kpi_employe(e):
    """Calcule les KPI d'un seul employé — fonction utilitaire interne"""
    heures_theoriques = e.heures_travail_semaine * 4
    taux_presence = round(
        (heures_theoriques - e.heures_absence_mois) / heures_theoriques * 100, 2
    )
    taux_ponctualite = round((22 - e.retards_mois) / 22 * 100, 2)
    score_rendement = round(
        e.taux_rendement * 0.40 +
        e.performance_moyenne * 0.35 +
        e.evaluation_manager * 0.15 +
        taux_ponctualite * 0.10, 2
    )
    fatigue_score = round(
        (
            e.retards_mois +
            e.heures_absence_mois / 8 +
            e.accidents_travail * 5 +
            e.maladies_professionnelles * 3
        ) / max(e.anciennete_annees, 1), 3
    )

    logs = FactoryLog.query.filter_by(employee_id=e.employee_id).all()
    total_taches      = len(logs)
    taches_completees = sum(1 for l in logs if l.task_status == "completed")
    anomalies         = sum(1 for l in logs if l.anomaly_flag == 1)
    taux_completion   = round(taches_completees / total_taches * 100, 2) if total_taches > 0 else 0
    taux_anomalies    = round(anomalies / total_taches * 100, 2) if total_taches > 0 else 0

    if score_rendement >= 80 and fatigue_score < 2:
        statut = "ok"
    elif score_rendement >= 60 and fatigue_score < 4:
        statut = "warning"
    else:
        statut = "critical"

    return {
        "employee_id":     e.employee_id,
        "nom":             e.nom,
        "prenom":          e.prenom,
        "poste":           e.poste,
        "departement":     e.departement,
        "shift":           e.shift_travail,
        "statut_presence": e.statut_presence,
        "kpi": {
            "taux_presence":    taux_presence,
            "taux_ponctualite": taux_ponctualite,
            "score_rendement":  score_rendement,
            "fatigue_score":    fatigue_score,
            "taux_completion":  taux_completion,
            "taux_anomalies":   taux_anomalies,
            "total_taches":     total_taches
        },
        "risques": {
            "risque_absenteisme": e.risque_absenteisme,
            "risque_depart":      e.risque_depart,
            "accidents_travail":  e.accidents_travail
        },
        "statut": statut
    }


def get_kpi_employes_today():
    """Tous les employés"""
    try:
        employes = Employee.query.all()
        if not employes:
            return {"statut": "vide", "message": "Aucun employé trouvé"}, 404

        result = [_calculer_kpi_employe(e) for e in employes]

        ordre = {"critical": 0, "warning": 1, "ok": 2}
        result.sort(key=lambda x: ordre[x["statut"]])
        return result
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_kpi_employe_by_id(employee_id):
    """1 employé précis par ID"""
    try:
        e = Employee.query.filter_by(employee_id=employee_id).first()
        if not e:
            return {"statut": "erreur", "message": f"Employé '{employee_id}' non trouvé"}, 404
        return _calculer_kpi_employe(e)
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_kpi_by_shift(shift):
    """Tous les employés d'un shift"""
    try:
        employes = Employee.query.filter_by(shift_travail=shift).all()
        if not employes:
            return {"statut": "erreur", "message": f"Aucun employé trouvé pour le shift '{shift}'"}, 404

        result = [_calculer_kpi_employe(e) for e in employes]

        ordre = {"critical": 0, "warning": 1, "ok": 2}
        result.sort(key=lambda x: ordre[x["statut"]])
        return result
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_kpi_by_departement(departement):
    """Tous les employés d'un département / atelier"""
    try:
        employes = Employee.query.filter_by(departement=departement).all()
        if not employes:
            return {"statut": "erreur", "message": f"Aucun employé trouvé pour le département '{departement}'"}, 404

        result = [_calculer_kpi_employe(e) for e in employes]

        ordre = {"critical": 0, "warning": 1, "ok": 2}
        result.sort(key=lambda x: ordre[x["statut"]])
        return result
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_kpi_shift_today():
    """KPI agrégé par shift pour aujourd'hui"""
    try:
        today = date.today()
        rows = DailyHrKpi.query.filter_by(date=today).all()
        if not rows:
            return {"statut": "vide", "message": "Pas encore calculé pour aujourd'hui"}, 404
        return [
            {
                "shift":                  r.shift,
                "present_count":          r.present_count,
                "absent_count":           r.absent_count,
                "absenteeism_rate":       r.absenteeism_rate,
                "avg_productivity":       r.avg_productivity,
                "avg_rendement":          r.avg_rendement,
                "fatigue_score":          r.fatigue_score,
                "rotation_risk_count":    r.rotation_risk_count,
                "absenteisme_risk_count": r.absenteisme_risk_count,
                "avg_seniority":          r.avg_seniority,
                "computed_at":            r.computed_at.isoformat()
            }
            for r in rows
        ]
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_kpi_hr_series(shift="ALL"):
    """Séries temporelles mois précédent vs mois actuel"""
    try:
        today = date.today()
        debut_mois_actuel    = today.replace(day=1)
        debut_mois_precedent = (debut_mois_actuel - timedelta(days=1)).replace(day=1)

        rows = DailyHrKpi.query.filter(
            DailyHrKpi.shift == shift,
            DailyHrKpi.date  >= debut_mois_precedent
        ).order_by(DailyHrKpi.date).all()

        previous_month = []
        current_month  = []

        for r in rows:
            point = {
                "date":                r.date.isoformat(),
                "absenteeism_rate":    r.absenteeism_rate,
                "avg_productivity":    r.avg_productivity,
                "avg_rendement":       r.avg_rendement,
                "fatigue_score":       r.fatigue_score,
                "rotation_risk_count": r.rotation_risk_count
            }
            if r.date < debut_mois_actuel:
                previous_month.append(point)
            else:
                current_month.append(point)

        return {
            "shift":          shift,
            "previous_month": previous_month,
            "current_month":  current_month
        }
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def get_hr_alerts(severity=None):
    """Alertes RH actives non lues"""
    try:
        query = HrAlert.query.filter_by(is_read=False).order_by(HrAlert.created_at.desc())
        if severity:
            query = query.filter_by(severity=severity)
        alerts = query.limit(50).all()
        return [
            {
                "id":          a.id,
                "date":        a.date.isoformat(),
                "employee_id": a.employee_id,
                "shift":       a.shift,
                "alert_type":  a.alert_type,
                "severity":    a.severity,
                "message":     a.message,
                "created_at":  a.created_at.isoformat()
            }
            for a in alerts
        ]
    except Exception as e:
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500


def mark_alert_read(alert_id):
    """Marquer une alerte comme lue"""
    try:
        a = HrAlert.query.get(alert_id)
        if not a:
            return {"statut": "erreur", "message": "Alerte non trouvée"}, 404
        a.is_read = True
        db.session.commit()
        return {"message": "Alerte marquée comme lue"}
    except Exception as e:
        db.session.rollback()
        return {"statut": "erreur", "message": str(e), "detail": traceback.format_exc()}, 500