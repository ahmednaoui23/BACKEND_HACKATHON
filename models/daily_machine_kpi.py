from config import db

class DailyMachineKpi(db.Model):
    __tablename__ = "daily_machine_kpi"

    id               = db.Column(db.Integer, primary_key=True)
    date             = db.Column(db.Date, nullable=False)
    machine_id       = db.Column(db.Text, nullable=False)
    mtbf             = db.Column(db.Float)
    mttr             = db.Column(db.Float)
    availability     = db.Column(db.Float)
    utilization_rate = db.Column(db.Float)
    anomaly_rate     = db.Column(db.Float)
    cost_estimate    = db.Column(db.Float)
    computed_at      = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f"<DailyMachineKpi {self.date} - {self.machine_id}>"