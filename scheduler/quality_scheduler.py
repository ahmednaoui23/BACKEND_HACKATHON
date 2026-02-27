from apscheduler.schedulers.background import BackgroundScheduler
from scheduler.quality_calculator import calculer_et_stocker_quality_kpi
from datetime import datetime

scheduler = BackgroundScheduler()

def start_quality_scheduler(app):
    def job():
        with app.app_context():
            try:
                calculer_et_stocker_quality_kpi()
            except Exception as e:
                print(f"[Quality Scheduler] ❌ Erreur job : {e}")

    scheduler.add_job(
        func             = job,
        trigger          = "interval",
        minutes          = 15,
        id               = "quality_kpi_realtime",
        next_run_time    = datetime.now(),
        replace_existing = True
    )
    scheduler.add_job(
        func             = job,
        trigger          = "cron",
        hour             = 2,
        minute           = 0,
        id               = "quality_kpi_nightly",
        replace_existing = True
    )
    scheduler.start()
    print("[Quality Scheduler] ✅ Démarré — interval 15min + cron 02h00")

def stop_quality_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("[Quality Scheduler] ⛔ Arrêté")