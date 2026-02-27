from config import db

class DailyHrKpi(db.Model):
    __tablename__ = "daily_hr_kpi"

    id                     = db.Column(db.Integer, primary_key=True)
    date                   = db.Column(db.Date, nullable=False)
    shift                  = db.Column(db.Text, nullable=False)
    present_count          = db.Column(db.Integer)
    absent_count           = db.Column(db.Integer)
    absenteeism_rate       = db.Column(db.Float)
    avg_productivity       = db.Column(db.Float)
    avg_rendement          = db.Column(db.Float)
    fatigue_score          = db.Column(db.Float)
    rotation_risk_count    = db.Column(db.Integer)
    absenteisme_risk_count = db.Column(db.Integer)
    avg_seniority          = db.Column(db.Float)
    computed_at            = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f"<DailyHrKpi {self.date} - {self.shift}>"