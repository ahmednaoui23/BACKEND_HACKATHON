from apscheduler.schedulers.background import BackgroundScheduler
from scheduler.machine_calculator import calculer_et_stocker_machine_kpi
from datetime import datetime

scheduler = BackgroundScheduler()


def start_machine_scheduler(app):
    """
    À appeler dans app.py après création de l'app Flask
    """

    def job():
        with app.app_context():
            try:
                calculer_et_stocker_machine_kpi()
            except Exception as e:
                print(f"[Machine Scheduler] ❌ Erreur job : {e}")

    # Toutes les 15 minutes — temps réel journée en cours
    scheduler.add_job(
        func             = job,
        trigger          = "interval",
        minutes          = 15,
        id               = "machine_kpi_realtime",
        next_run_time    = datetime.now(),
        replace_existing = True
    )

    # Chaque nuit à 01h30 — consolidation propre
    scheduler.add_job(
        func             = job,
        trigger          = "cron",
        hour             = 1,
        minute           = 30,
        id               = "machine_kpi_nightly",
        replace_existing = True
    )

    scheduler.start()
    print("[Machine Scheduler] ✅ Démarré — interval 15min + cron 01h30")


def stop_machine_scheduler():
    """
    Arrêter proprement le scheduler
    """
    if scheduler.running:
        scheduler.shutdown()
        print("[Machine Scheduler] ⛔ Arrêté")