from flask import Flask
from flask_cors import CORS
from config import db, Config

from routes.employe_routes import employe_bp
from routes.machine_routes import machine_bp
from routes.atelier_routes import atelier_bp
from routes.taches_routes import taches_bp
from routes.usine_routes import usine_bp
from routes.global_routes import global_bp
from routes.quality_routes import quality_bp
from routes.production_routes import production_bp

from scheduler.hr_scheduler import start_hr_scheduler, stop_hr_scheduler
from scheduler.machine_scheduler import start_machine_scheduler, stop_machine_scheduler
from scheduler.quality_scheduler import start_quality_scheduler, stop_quality_scheduler
from scheduler.production_scheduler import start_production_scheduler, stop_production_scheduler
import atexit

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.register_blueprint(employe_bp)
app.register_blueprint(machine_bp)
app.register_blueprint(atelier_bp)
app.register_blueprint(taches_bp)
app.register_blueprint(usine_bp)
app.register_blueprint(global_bp)
app.register_blueprint(quality_bp)
app.register_blueprint(production_bp)

if __name__ == "__main__":
    with app.app_context():
        from models.daily_hr_kpi import DailyHrKpi
        from models.hr_alert import HrAlert
        from models.daily_machine_kpi import DailyMachineKpi
        from models.machine_alert import MachineAlert
        from models.daily_quality_kpi import DailyQualityKpi
        from models.quality_alert import QualityAlert
        from models.daily_production_kpi import DailyProductionKpi
        from models.production_alert import ProductionAlert

        DailyHrKpi.__table__.create(bind=db.engine, checkfirst=True)
        HrAlert.__table__.create(bind=db.engine, checkfirst=True)
        DailyMachineKpi.__table__.create(bind=db.engine, checkfirst=True)
        MachineAlert.__table__.create(bind=db.engine, checkfirst=True)
        DailyQualityKpi.__table__.create(bind=db.engine, checkfirst=True)
        QualityAlert.__table__.create(bind=db.engine, checkfirst=True)
        DailyProductionKpi.__table__.create(bind=db.engine, checkfirst=True)
        ProductionAlert.__table__.create(bind=db.engine, checkfirst=True)
        print("✅ Toutes les tables créées")

    start_hr_scheduler(app)
    start_machine_scheduler(app)
    start_quality_scheduler(app)
    start_production_scheduler(app)

    atexit.register(stop_hr_scheduler)
    atexit.register(stop_machine_scheduler)
    atexit.register(stop_quality_scheduler)
    atexit.register(stop_production_scheduler)

    app.run(debug=True, host="0.0.0.0", port=5000)
