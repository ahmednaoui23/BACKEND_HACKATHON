from config import db

class DailyQualityKpi(db.Model):
    __tablename__ = "daily_quality_kpi"

    id                 = db.Column(db.Integer, primary_key=True)
    date               = db.Column(db.Date, nullable=False)
    machine_id         = db.Column(db.Text)
    anomaly_rate       = db.Column(db.Float)
    first_pass_quality = db.Column(db.Float)
    rejection_rate     = db.Column(db.Float)
    dpmo               = db.Column(db.Float)
    stability          = db.Column(db.Float)
    computed_at        = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f"<DailyQualityKpi {self.date} - {self.machine_id}>"