from config import db

class DailyProductionKpi(db.Model):
    __tablename__ = "daily_production_kpi"

    id                = db.Column(db.Integer, primary_key=True)
    date              = db.Column(db.Date, nullable=False)
    shift             = db.Column(db.Text, nullable=False)
    atelier           = db.Column(db.Text, nullable=False, default="ALL")
    taux_completion   = db.Column(db.Float)
    efficiency        = db.Column(db.Float)
    stability         = db.Column(db.Float)
    global_yield      = db.Column(db.Float)
    oee               = db.Column(db.Float)
    duration_ratio    = db.Column(db.Float)
    cadence           = db.Column(db.Float)
    interruption_rate = db.Column(db.Float)
    computed_at       = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f"<DailyProductionKpi {self.date} - {self.shift} - {self.atelier}>"