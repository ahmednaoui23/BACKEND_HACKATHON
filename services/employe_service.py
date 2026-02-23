from config import db
from models.employee import Employee
from models.factory_log import FactoryLog
from sqlalchemy import func

def get_rendement_employe(employee_id):
    e = Employee.query.filter_by(employee_id=employee_id).first()
    if not e:
        return {"error": "Employé non trouvé"}

    # NORMAL
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

    # tâches depuis factory_logs
    logs = FactoryLog.query.filter_by(employee_id=employee_id).all()
    total_taches = len(logs)
    taches_completees = sum(1 for l in logs if l.task_status == "completed")
    taux_anomalies = round(sum(1 for l in logs if l.anomaly_flag == 1) / total_taches * 100, 2) if total_taches > 0 else 0

    # classement dans atelier
    employes_atelier = Employee.query.filter_by(departement=e.departement).all()
    scores = []
    for emp in employes_atelier:
        tp = (emp.heures_travail_semaine * 4 - emp.heures_absence_mois) / (emp.heures_travail_semaine * 4) * 100
        sc = emp.taux_rendement * 0.40 + emp.performance_moyenne * 0.35 + emp.evaluation_manager * 0.15 + tp * 0.10
        scores.append((emp.employee_id, sc))
    scores.sort(key=lambda x: x[1], reverse=True)
    classement = next((i+1 for i, s in enumerate(scores) if s[0] == employee_id), None)

    # shift le plus productif
    shift_stats = {}
    for l in logs:
        if l.task_status == "completed":
            shift_stats[l.shift] = shift_stats.get(l.shift, 0) + 1
    meilleur_shift = max(shift_stats, key=shift_stats.get) if shift_stats else None

    # CACHÉ
    indice_epuisement = None  # nécessite données semaine par semaine
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


def get_historique_employe(employee_id):
    # retourne les données disponibles pour tracer une évolution
    e = Employee.query.filter_by(employee_id=employee_id).first()
    if not e:
        return {"error": "Employé non trouvé"}
    return {
        "employee_id": employee_id,
        "performance_moyenne": e.performance_moyenne,
        "taux_rendement": e.taux_rendement,
        "evaluation_manager": e.evaluation_manager,
        "note": "Connecter à un historique mensuel pour courbe évolution"
    }