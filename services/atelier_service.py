from config import db
from models.machine import Machine
from models.employee import Employee
from models.factory_log import FactoryLog
import statistics

def _score_employe(e):
    taux_ponctualite = (22 - e.retards_mois) / 22 * 100
    return round(
        e.taux_rendement * 0.40 +
        e.performance_moyenne * 0.35 +
        e.evaluation_manager * 0.15 +
        taux_ponctualite * 0.10, 2
    )

def _oee_machine(m):
    td = (30 - m.pannes_mois) / 30 * 100
    tu = m.temps_total_tache_min / (m.capacite * m.temps_par_unite_min) * 100 if m.capacite and m.temps_par_unite_min else 0
    return round(td * tu * m.rendement_machine / 10000, 2)

def get_rendement_atelier(nom):
    machines = Machine.query.filter_by(atelier=nom).all()
    employes = Employee.query.filter_by(departement=nom).all()

    if not machines and not employes:
        return {"error": "Atelier non trouvé"}

    # NORMAL
    oee_list = [_oee_machine(m) for m in machines]
    score_list = [_score_employe(e) for e in employes]
    moyenne_oee = round(statistics.mean(oee_list), 2) if oee_list else 0
    moyenne_score = round(statistics.mean(score_list), 2) if score_list else 0
    rendement_atelier = round(moyenne_oee * 0.50 + moyenne_score * 0.50, 2)

    machines_actives = sum(1 for m in machines if m.etat_machine == "actif")
    machines_en_panne = sum(1 for m in machines if m.etat_machine == "en panne")

    machine_ids = [m.machine_id for m in machines]
    logs = FactoryLog.query.filter(FactoryLog.machine_id.in_(machine_ids)).all()
    total_logs = len(logs)
    taux_completion = round(sum(1 for l in logs if l.task_status == "completed") / total_logs * 100, 2) if total_logs > 0 else 0
    taux_anomalies = round(sum(1 for l in logs if l.anomaly_flag == 1) / total_logs * 100, 2) if total_logs > 0 else 0

    shift_stats = {}
    for l in logs:
        if l.task_status == "completed":
            shift_stats[l.shift] = shift_stats.get(l.shift, 0) + 1
    meilleur_shift = max(shift_stats, key=shift_stats.get) if shift_stats else None

    # benchmark vs autres ateliers
    tous_ateliers = db.session.query(Machine.atelier).distinct().all()
    tous_ateliers = [a[0] for a in tous_ateliers]
    benchmark = {}
    for at in tous_ateliers:
        mach = Machine.query.filter_by(atelier=at).all()
        oees = [_oee_machine(m) for m in mach]
        benchmark[at] = round(statistics.mean(oees), 2) if oees else 0
    max_rendement = max(benchmark.values()) if benchmark else 1
    benchmark_relatif = round(rendement_atelier / max_rendement * 100, 2)

    # CACHÉ
    taches_par_machine = {}
    for l in logs:
        taches_par_machine[l.machine_id] = taches_par_machine.get(l.machine_id, 0) + 1
    equilibre_charge = round(statistics.stdev(list(taches_par_machine.values())), 2) if len(taches_par_machine) > 1 else 0
    indice_chaleur = round(
        taux_completion * moyenne_oee / (machines_en_panne + taux_anomalies + 1), 2
    )

    return {
        "info": {
            "atelier": nom,
            "nombre_machines": len(machines),
            "nombre_employes": len(employes)
        },
        "normal": {
            "rendement_atelier": rendement_atelier,
            "moyenne_oee_machines": moyenne_oee,
            "moyenne_score_employes": moyenne_score,
            "machines_actives": machines_actives,
            "machines_en_panne": machines_en_panne,
            "taux_completion": taux_completion,
            "taux_anomalies": taux_anomalies,
            "meilleur_shift": meilleur_shift,
            "benchmark_relatif": f"{benchmark_relatif}% du meilleur atelier"
        },
        "cache": {
            "equilibre_charge": equilibre_charge,
            "indice_chaleur_productive": indice_chaleur
        }
    }

def get_top10_atelier(nom):
    employes = Employee.query.filter_by(departement=nom).all()
    scores = [{"employee_id": e.employee_id, "nom": e.nom, "prenom": e.prenom,
               "poste": e.poste, "score": _score_employe(e)} for e in employes]
    scores.sort(key=lambda x: x["score"], reverse=True)
    return {"atelier": nom, "top10": scores[:10]}

def get_flop10_atelier(nom):
    employes = Employee.query.filter_by(departement=nom).all()
    scores = [{"employee_id": e.employee_id, "nom": e.nom, "prenom": e.prenom,
               "poste": e.poste, "score": _score_employe(e)} for e in employes]
    scores.sort(key=lambda x: x["score"])
    return {"atelier": nom, "flop10": scores[:10]}