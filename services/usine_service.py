from models.machine import Machine
from models.employee import Employee
from models.factory_log import FactoryLog
from config import db
import statistics
import traceback

def _oee_machine(m):
    try:
        td = (30 - m.pannes_mois) / 30 * 100
        tu = m.temps_total_tache_min / (m.capacite * m.temps_par_unite_min) * 100 if m.capacite and m.temps_par_unite_min else 0
        return td * tu * m.rendement_machine / 10000
    except Exception as e:
        return 0

def _score_employe(e):
    try:
        tp = (22 - e.retards_mois) / 22 * 100
        return e.taux_rendement * 0.40 + e.performance_moyenne * 0.35 + e.evaluation_manager * 0.15 + tp * 0.10
    except Exception as e:
        return 0

def get_rendement_usine():
    try:
        machines = Machine.query.all()
        employes = Employee.query.all()
        logs = FactoryLog.query.all()

        if not machines:
            return {"statut": "erreur", "message": "Aucune machine trouvée dans la base de données"}, 404
        if not employes:
            return {"statut": "erreur", "message": "Aucun employé trouvé dans la base de données"}, 404

        oee_list = [_oee_machine(m) for m in machines]
        score_list = [_score_employe(e) for e in employes]
        rendement_global = round(
            statistics.mean(oee_list) * 0.50 + statistics.mean(score_list) * 0.50, 2
        ) if oee_list and score_list else 0

        capacite_totale = sum(m.capacite for m in machines)
        production_reelle = sum(1 for l in logs if l.task_status == "completed")
        taux_gaspillage = round((capacite_totale - production_reelle) / max(capacite_totale, 1) * 100, 2)

        ateliers = db.session.query(Machine.atelier).distinct().all()
        ateliers = [a[0] for a in ateliers]
        atelier_rendements = {}
        for at in ateliers:
            mach = Machine.query.filter_by(atelier=at).all()
            oees = [_oee_machine(m) for m in mach]
            atelier_rendements[at] = round(statistics.mean(oees), 2) if oees else 0

        meilleur_atelier = max(atelier_rendements, key=atelier_rendements.get) if atelier_rendements else None
        pire_atelier = min(atelier_rendements, key=atelier_rendements.get) if atelier_rendements else None

        total_logs = len(logs)
        taux_completion = round(sum(1 for l in logs if l.task_status == "completed") / total_logs * 100, 2) if total_logs > 0 else 0
        taux_anomalies = round(sum(1 for l in logs if l.anomaly_flag == 1) / total_logs * 100, 2) if total_logs > 0 else 0
        rendement_resilience = round(rendement_global * (1 - taux_anomalies / 100), 2)

        return {
            "normal": {
                "rendement_global_usine": rendement_global,
                "taux_gaspillage_capacite": taux_gaspillage,
                "taux_completion_global": taux_completion,
                "taux_anomalies_global": taux_anomalies,
                "meilleur_atelier": {"nom": meilleur_atelier, "rendement": atelier_rendements.get(meilleur_atelier, 0)},
                "atelier_plus_degrade": {"nom": pire_atelier, "rendement": atelier_rendements.get(pire_atelier, 0)},
                "rendement_par_atelier": atelier_rendements
            },
            "cache": {
                "rendement_resilience": rendement_resilience
            }
        }
    except Exception as e:
        return {
            "statut": "erreur",
            "message": str(e),
            "detail": traceback.format_exc()
        }, 500


def get_pouls_usine():
    try:
        employes = Employee.query.all()
        machines = Machine.query.all()
        logs = FactoryLog.query.all()
        total_logs = len(logs)

        if not employes:
            return {"statut": "erreur", "message": "Aucun employé trouvé dans la base de données"}, 404
        if not machines:
            return {"statut": "erreur", "message": "Aucune machine trouvée dans la base de données"}, 404

        return {
            "total_employes": len(employes),
            "employes_presents": sum(1 for e in employes if e.statut_presence == "présent"),
            "employes_absents": sum(1 for e in employes if e.statut_presence == "absent"),
            "total_machines": len(machines),
            "machines_actives": sum(1 for m in machines if m.etat_machine == "actif"),
            "machines_en_panne": sum(1 for m in machines if m.etat_machine == "en panne"),
            "taux_completion_jour": round(sum(1 for l in logs if l.task_status == "completed") / max(total_logs, 1) * 100, 2),
            "taux_anomalies_jour": round(sum(1 for l in logs if l.anomaly_flag == 1) / max(total_logs, 1) * 100, 2)
        }
    except Exception as e:
        return {
            "statut": "erreur",
            "message": str(e),
            "detail": traceback.format_exc()
        }, 500


def get_carte_risques():
    try:
        employes = Employee.query.all()
        machines = Machine.query.all()

        if not employes:
            return {"statut": "erreur", "message": "Aucun employé trouvé dans la base de données"}, 404
        if not machines:
            return {"statut": "erreur", "message": "Aucune machine trouvée dans la base de données"}, 404

        employes_risque = [
            {"employee_id": e.employee_id, "nom": e.nom, "prenom": e.prenom,
             "risque_depart": e.risque_depart, "risque_absenteisme": e.risque_absenteisme}
            for e in employes if e.risque_depart == "élevé" or e.risque_absenteisme == "élevé"
        ]
        machines_risque = [
            {"machine_id": m.machine_id, "nom_machine": m.nom_machine, "atelier": m.atelier,
             "pannes_mois": m.pannes_mois, "etat_machine": m.etat_machine}
            for m in machines if m.etat_machine == "en panne" or m.pannes_mois > 3
        ]

        return {
            "employes_a_risque": employes_risque,
            "machines_a_risque": machines_risque
        }
    except Exception as e:
        return {
            "statut": "erreur",
            "message": str(e),
            "detail": traceback.format_exc()
        }, 500


def get_rapport_mensuel():
    try:
        employes = Employee.query.all()
        machines = Machine.query.all()
        logs = FactoryLog.query.all()
        total_logs = len(logs)

        if not employes:
            return {"statut": "erreur", "message": "Aucun employé trouvé dans la base de données"}, 404
        if not machines:
            return {"statut": "erreur", "message": "Aucune machine trouvée dans la base de données"}, 404

        produit_stats = {}
        for l in logs:
            if l.product not in produit_stats:
                produit_stats[l.product] = 0
            if l.task_status == "completed":
                produit_stats[l.product] += 1

        return {
            "total_employes": len(employes),
            "masse_salariale_totale": sum(e.salaire_mensuel for e in employes),
            "total_machines": len(machines),
            "machines_en_panne": sum(1 for m in machines if m.etat_machine == "en panne"),
            "total_taches": total_logs,
            "taches_completees": sum(1 for l in logs if l.task_status == "completed"),
            "taux_completion": round(sum(1 for l in logs if l.task_status == "completed") / max(total_logs, 1) * 100, 2),
            "taux_anomalies": round(sum(1 for l in logs if l.anomaly_flag == 1) / max(total_logs, 1) * 100, 2),
            "production_par_produit": produit_stats,
            "absenteisme_moyen": round(sum(e.heures_absence_mois for e in employes) / max(len(employes), 1), 2)
        }
    except Exception as e:
        return {
            "statut": "erreur",
            "message": str(e),
            "detail": traceback.format_exc()
        }, 500