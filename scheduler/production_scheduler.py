from apscheduler.schedulers.background import BackgroundScheduler
from scheduler.production_calculator import calculer_et_stocker_production_kpi
from datetime import datetime

scheduler = BackgroundScheduler()

def start_production_scheduler(app):
    def job():
        with app.app_context():
            try:
                calculer_et_stocker_production_kpi()
            except Exception as e:
                print(f"[Production Scheduler] ❌ Erreur job : {e}")

    scheduler.add_job(
        func             = job,
        trigger          = "interval",
        minutes          = 15,
        id               = "production_kpi_realtime",
        next_run_time    = datetime.now(),
        replace_existing = True
    )
    scheduler.add_job(
        func             = job,
        trigger          = "cron",
        hour             = 0,
        minute           = 30,
        id               = "production_kpi_nightly",
        replace_existing = True
    )
    scheduler.start()
    print("[Production Scheduler] ✅ Démarré — interval 15min + cron 00h30")

def stop_production_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("[Production Scheduler] ⛔ Arrêté")