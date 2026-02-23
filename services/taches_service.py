from models.factory_log import FactoryLog
from models.machine import Machine
from sqlalchemy import func
from config import db
import statistics

def get_rendement_taches():
    logs = FactoryLog.query.limit(100).all()
    total = len(logs)
    if total == 0:
        return {"error": "Aucune tâche trouvée"}

    # NORMAL
    taux_completion = round(sum(1 for l in logs if l.task_status == "completed") / total * 100, 2)
    taux_anomalies = round(sum(1 for l in logs if l.anomaly_flag == 1) / total * 100, 2)

    # efficacité temps réel
    efficacites = []
    for l in logs:
        m = Machine.query.filter_by(machine_id=l.machine_id).first()
        if m and l.task_duration_min and l.task_duration_min > 0:
            efficacites.append(m.temps_par_unite_min / l.task_duration_min * 100)
    efficacite_moyenne = round(statistics.mean(efficacites), 2) if efficacites else 0

    # rendement par produit
    produit_stats = {}
    for l in logs:
        if l.product not in produit_stats:
            produit_stats[l.product] = {"completed": 0, "duree_totale": 0}
        if l.task_status == "completed":
            produit_stats[l.product]["completed"] += 1
        produit_stats[l.product]["duree_totale"] += l.task_duration_min or 0
    rendement_par_produit = {
        p: round(v["completed"] / max(v["duree_totale"], 1) * 100, 4)
        for p, v in produit_stats.items()
    }

    # CACHÉ
    taux_premiere_reussite = round(
        sum(1 for l in logs if l.task_status == "completed" and l.anomaly_flag == 0) / total * 100, 2
    )

    shift_stats = {}
    for l in logs:
        if l.shift not in shift_stats:
            shift_stats[l.shift] = {"total": 0, "completed": 0}
        shift_stats[l.shift]["total"] += 1
        if l.task_status == "completed":
            shift_stats[l.shift]["completed"] += 1
    rendement_par_shift = {
        s: round(v["completed"] / max(v["total"], 1) * 100, 2)
        for s, v in shift_stats.items()
    }

    # débit horaire
    durees_shifts = {}
    for l in logs:
        durees_shifts[l.shift] = durees_shifts.get(l.shift, 0) + (l.task_duration_min or 0)
    debit_par_shift = {
        s: round(shift_stats[s]["completed"] / max(durees_shifts[s] / 60, 1), 2)
        for s in shift_stats
    }

    return {
        "normal": {
            "taux_completion_global": taux_completion,
            "taux_anomalies_global": taux_anomalies,
            "efficacite_temps_reel": efficacite_moyenne,
            "rendement_par_produit": rendement_par_produit
        },
        "cache": {
            "taux_premiere_reussite": taux_premiere_reussite,
            "rendement_par_shift": rendement_par_shift,
            "debit_horaire_par_shift": debit_par_shift
        }
    }