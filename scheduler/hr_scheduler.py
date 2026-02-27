from apscheduler.schedulers.background import BackgroundScheduler
from scheduler.hr_calculator import calculer_et_stocker_hr_kpi
from datetime import datetime

scheduler = BackgroundScheduler()


def start_hr_scheduler(app):
    """
    À appeler dans app.py après création de l'app Flask
    """

    def job():
        with app.app_context():
            try:
                calculer_et_stocker_hr_kpi()
            except Exception as e:
                print(f"[HR Scheduler] ❌ Erreur job : {e}")

    # Toutes les 15 minutes — temps réel journée en cours
    scheduler.add_job(
        func             = job,
        trigger          = "interval",
        minutes          = 15,
        id               = "hr_kpi_realtime",
        next_run_time    = datetime.now(),   # ← exécution immédiate au démarrage
        replace_existing = True
    )

    # Chaque nuit à 01h00 — consolidation propre
    scheduler.add_job(
        func             = job,
        trigger          = "cron",
        hour             = 1,
        minute           = 0,
        id               = "hr_kpi_nightly",
        replace_existing = True
    )

    scheduler.start()
    print("[HR Scheduler] ✅ Démarré — interval 15min + cron 01h00")


def stop_hr_scheduler():
    """
    Arrêter proprement le scheduler
    """
    if scheduler.running:
        scheduler.shutdown()
        print("[HR Scheduler] ⛔ Arrêté")