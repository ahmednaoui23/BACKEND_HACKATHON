from services.usine_service import get_rendement_usine
from services.taches_service import get_rendement_taches
from models.machine import Machine
from models.employee import Employee
from config import db
import statistics
import traceback

def _oee_machine(m):
    try:
        td = (30 - m.pannes_mois) / 30 * 100
        tu = m.temps_total_tache_min / (m.capacite * m.temps_par_unite_min) * 100 if m.capacite and m.temps_par_unite_min else 0
        return td * tu * m.rendement_machine / 10000
    except:
        return 0

def _score_employe(e):
    try:
        tp = (22 - e.retards_mois) / 22 * 100
        return e.taux_rendement * 0.40 + e.performance_moyenne * 0.35 + e.evaluation_manager * 0.15 + tp * 0.10
    except:
        return 0

def get_rendement_global():
    try:
        # usine
        usine = get_rendement_usine()
        if isinstance(usine, tuple) and usine[1] != 200:
            return {"statut": "erreur", "message": "Erreur lors du calcul du rendement usine", "detail": usine}, 500

        # taches
        taches = get_rendement_taches()
        if isinstance(taches, tuple) and taches[1] != 200:
            return {"statut": "erreur", "message": "Erreur lors du calcul des tâches", "detail": taches}, 500

        # résumé tous les ateliers
        ateliers = db.session.query(Machine.atelier).distinct().all()
        ateliers = [a[0] for a in ateliers]

        if not ateliers:
            return {"statut": "erreur", "message": "Aucun atelier trouvé dans la base de données"}, 404

        resume_ateliers = {}
        for at in ateliers:
            mach = Machine.query.filter_by(atelier=at).all()
            emps = Employee.query.filter_by(departement=at).all()
            oees = [_oee_machine(m) for m in mach]
            scores = [_score_employe(e) for e in emps]
            resume_ateliers[at] = {
                "rendement_machines": round(statistics.mean(oees), 2) if oees else 0,
                "rendement_employes": round(statistics.mean(scores), 2) if scores else 0,
                "nombre_machines": len(mach),
                "nombre_employes": len(emps)
            }

        # résumé tous les employés
        employes = Employee.query.limit(10).all()
        if not employes:
            return {"statut": "erreur", "message": "Aucun employé trouvé dans la base de données"}, 404

        resume_employes = sorted([
            {
                "employee_id": e.employee_id,
                "nom": e.nom,
                "prenom": e.prenom,
                "departement": e.departement,
                "score": round(_score_employe(e), 2)
            }
            for e in employes
        ], key=lambda x: x["score"], reverse=True)

        # résumé toutes les machines
        machines = Machine.query.limit(10).all()
        if not machines:
            return {"statut": "erreur", "message": "Aucune machine trouvée dans la base de données"}, 404

        resume_machines = sorted([
            {
                "machine_id": m.machine_id,
                "nom_machine": m.nom_machine,
                "atelier": m.atelier,
                "oee": round(_oee_machine(m), 2),
                "etat_machine": m.etat_machine
            }
            for m in machines
        ], key=lambda x: x["oee"], reverse=True)

        return {
            "usine": usine,
            "taches": taches,
            "ateliers": resume_ateliers,
            "top_employes": resume_employes[:10],
            "top_machines": resume_machines[:10],
            "flop_employes": resume_employes[-10:],
            "flop_machines": resume_machines[-10:]
        }
    except Exception as e:
        return {
            "statut": "erreur",
            "message": str(e),
            "detail": traceback.format_exc()
        }, 500