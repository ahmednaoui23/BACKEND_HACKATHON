from config import db
from models.machine import Machine
from models.factory_log import FactoryLog
from models.employee import Employee
import traceback

def get_rendement_machine(machine_id):
    try:
        m = Machine.query.filter_by(machine_id=machine_id).first()
        if not m:
            return {"statut": "erreur", "message": f"Machine avec l'id '{machine_id}' non trouvée"}, 404

        taux_disponibilite = round((30 - m.pannes_mois) / 30 * 100, 2)
        taux_utilisation = round(
            m.temps_total_tache_min / (m.capacite * m.temps_par_unite_min) * 100, 2
        ) if m.capacite and m.temps_par_unite_min else 0
        oee = round(taux_disponibilite * taux_utilisation * m.rendement_machine / 10000, 2)

        machines_atelier = Machine.query.filter_by(atelier=m.atelier).all()
        oee_list = []
        for mac in machines_atelier:
            td = (30 - mac.pannes_mois) / 30 * 100
            tu = mac.temps_total_tache_min / (mac.capacite * mac.temps_par_unite_min) * 100 if mac.capacite and mac.temps_par_unite_min else 0
            o = td * tu * mac.rendement_machine / 10000
            oee_list.append((mac.machine_id, o))
        oee_list.sort(key=lambda x: x[1], reverse=True)
        classement = next((i+1 for i, s in enumerate(oee_list) if s[0] == machine_id), None)

        logs = FactoryLog.query.filter_by(machine_id=machine_id).all()
        emp_stats = {}
        for l in logs:
            if l.task_status == "completed":
                emp_stats[l.employee_id] = emp_stats.get(l.employee_id, 0) + 1
        top5 = sorted(emp_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        top5_details = []
        for emp_id, count in top5:
            emp = Employee.query.filter_by(employee_id=emp_id).first()
            if emp:
                top5_details.append({
                    "employee_id": emp_id,
                    "nom": emp.nom,
                    "prenom": emp.prenom,
                    "taches_completees": count
                })

        indice_degradation = round(
            m.pannes_mois * (2026 - m.annee_installation) / max(m.rendement_machine, 0.1), 2
        )
        try:
            energie_val = float(m.consommation_energie)
            rendement_energetique = round(m.capacite / energie_val, 2)
        except:
            rendement_energetique = None

        total_logs = len(logs)
        taux_anomalies = round(sum(1 for l in logs if l.anomaly_flag == 1) / total_logs * 100, 2) if total_logs > 0 else 0
        indice_impact_panne = round(
            (sum(1 for l in logs if l.anomaly_flag == 1) / max(total_logs, 1)) * m.pannes_mois, 2
        )

        return {
            "info": {
                "machine_id": m.machine_id,
                "nom_machine": m.nom_machine,
                "type_machine": m.type_machine,
                "atelier": m.atelier,
                "marque": m.marque,
                "etat_machine": m.etat_machine,
                "annee_installation": m.annee_installation
            },
            "normal": {
                "taux_disponibilite": taux_disponibilite,
                "taux_utilisation": taux_utilisation,
                "oee": oee,
                "classement_atelier": f"{classement} / {len(oee_list)}",
                "top5_employes": top5_details
            },
            "cache": {
                "indice_degradation": indice_degradation,
                "rendement_energetique": rendement_energetique,
                "taux_anomalies": taux_anomalies,
                "indice_impact_panne": indice_impact_panne
            }
        }
    except Exception as e:
        return {
            "statut": "erreur",
            "message": str(e),
            "detail": traceback.format_exc()
        }, 500


def get_all_machines(atelier=None, etat=None):
    try:
        query = Machine.query
        if atelier:
            query = query.filter_by(atelier=atelier)
        if etat:
            query = query.filter_by(etat_machine=etat)
        machines = query.all()
        if not machines:
            return {"statut": "erreur", "message": "Aucune machine trouvée avec ces filtres"}, 404
        return [
            {
                "machine_id": m.machine_id,
                "nom_machine": m.nom_machine,
                "type_machine": m.type_machine,
                "atelier": m.atelier,
                "marque": m.marque,
                "etat_machine": m.etat_machine,
                "annee_installation": m.annee_installation,
                "capacite": m.capacite,
                "pannes_mois": m.pannes_mois,
                "rendement_machine": m.rendement_machine,
                "consommation_energie": m.consommation_energie
            }
            for m in machines
        ]
    except Exception as e:
        return {
            "statut": "erreur",
            "message": str(e),
            "detail": traceback.format_exc()
        }, 500


def get_machine_by_id(machine_id):
    try:
        m = Machine.query.filter_by(machine_id=machine_id).first()
        if not m:
            return {"statut": "erreur", "message": f"Machine avec l'id '{machine_id}' non trouvée"}, 404
        return {
            "machine_id": m.machine_id,
            "nom_machine": m.nom_machine,
            "type_machine": m.type_machine,
            "atelier": m.atelier,
            "tache": m.tache,
            "unite_production": m.unite_production,
            "capacite": m.capacite,
            "temps_par_unite_min": m.temps_par_unite_min,
            "temps_total_tache_min": m.temps_total_tache_min,
            "operateurs_requis": m.operateurs_requis,
            "pannes_mois": m.pannes_mois,
            "etat_machine": m.etat_machine,
            "annee_installation": m.annee_installation,
            "marque": m.marque,
            "consommation_energie": m.consommation_energie,
            "rendement_machine": m.rendement_machine
        }
    except Exception as e:
        return {
            "statut": "erreur",
            "message": str(e),
            "detail": traceback.format_exc()
        }, 500


def create_machine(data):
    try:
        m = Machine(**data)
        db.session.add(m)
        db.session.commit()
        return {"message": "Machine créée avec succès", "machine_id": m.machine_id}
    except Exception as e:
        db.session.rollback()
        return {
            "statut": "erreur",
            "message": str(e),
            "detail": traceback.format_exc()
        }, 500


def update_machine(machine_id, data):
    try:
        m = Machine.query.filter_by(machine_id=machine_id).first()
        if not m:
            return {"statut": "erreur", "message": f"Machine avec l'id '{machine_id}' non trouvée"}, 404
        for key, value in data.items():
            setattr(m, key, value)
        db.session.commit()
        return {"message": "Machine mise à jour avec succès"}
    except Exception as e:
        db.session.rollback()
        return {
            "statut": "erreur",
            "message": str(e),
            "detail": traceback.format_exc()
        }, 500


def delete_machine(machine_id):
    try:
        m = Machine.query.filter_by(machine_id=machine_id).first()
        if not m:
            return {"statut": "erreur", "message": f"Machine avec l'id '{machine_id}' non trouvée"}, 404
        db.session.delete(m)
        db.session.commit()
        return {"message": "Machine supprimée avec succès"}
    except Exception as e:
        db.session.rollback()
        return {
            "statut": "erreur",
            "message": str(e),
            "detail": traceback.format_exc()
        }, 500