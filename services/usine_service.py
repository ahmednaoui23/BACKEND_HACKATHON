from models.machine import Machine
from models.employee import Employee
from models.factory_log import FactoryLog
from config import db
import statistics

def _oee_machine(m):
    td = (30 - m.pannes_mois) / 30 * 100
    tu = m.temps_total_tache_min / (m.capacite * m.temps_par_unite_min) * 100 if m.capacite and m.temps_par_unite_min else 0
    return td * tu * m.rendement_machine / 10000

def _score_employe(e):
    tp = (22 - e.retards_mois) / 22 * 100
    return e.taux_rendement * 0.40 + e.performance_moyenne * 0.35 + e.evaluation_manager * 0.15 + tp * 0.10

def get_rendement_usine():
    machines = Machine.query.all()
    employes = Employee.query.all()
    logs = FactoryLog.query.all()

    # NORMAL
    oee_list = [_oee_machine(m) for m in machines]
    score_list = [_score_employe(e) for e in employes]
    rendement_global = round(
        statistics.mean(oee_list) * 0.50 + statistics.mean(score_list) * 0.50, 2
    ) if oee_list and score_list else 0

    capacite_totale = sum(m.capacite for m in machines)
    production_reelle = sum(1 for l in logs if l.task_status == "completed")
    taux_gaspillage = round((capacite_totale - production_reelle) / max(capacite_totale, 1) * 100, 2)

    # meilleur et pire atelier
    ateliers = db.session.query(Machine.atelier).distinct().all()
    ateliers = [a[0] for a in ateliers]
    atelier_rendements = {}
    for at in ateliers:
        mach = Machine.query.filter_by(atelier=at).all()
        oees = [_oee_machine(m) for m in mach]
        atelier_rendements[at] = round(statistics.mean(oees), 2) if oees else 0
    meilleur_atelier = max(atelier_rendements, key=atelier_rendements.get)
    pire_atelier = min(atelier_rendements, key=atelier_rendements.get)

    total_logs = len(logs)
    taux_completion = round(sum(1 for l in logs if l.task_status == "completed") / total_logs * 100, 2) if total_logs > 0 else 0
    taux_anomalies = round(sum(1 for l in logs if l.anomaly_flag == 1) / total_logs * 100, 2) if total_logs > 0 else 0

    # CACHÉ
    rendement_resilience = round(rendement_global * (1 - taux_anomalies / 100), 2)

    return {
        "normal": {
            "rendement_global_usine": rendement_global,
            "taux_gaspillage_capacite": taux_gaspillage,
            "taux_completion_global": taux_completion,
            "taux_anomalies_global": taux_anomalies,
            "meilleur_atelier": {"nom": meilleur_atelier, "rendement": atelier_rendements[meilleur_atelier]},
            "atelier_plus_degrade": {"nom": pire_atelier, "rendement": atelier_rendements[pire_atelier]},
            "rendement_par_atelier": atelier_rendements
        },
        "cache": {
            "rendement_resilience": rendement_resilience
        }
    }