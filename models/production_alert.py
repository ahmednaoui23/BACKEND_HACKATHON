from config import db

class ProductionAlert(db.Model):
    __tablename__ = "production_alerts"

    id         = db.Column(db.Integer, primary_key=True)
    date       = db.Column(db.Date, nullable=False)
    shift      = db.Column(db.Text)
    atelier    = db.Column(db.Text)
    alert_type = db.Column(db.Text)
    severity   = db.Column(db.Text)
    message    = db.Column(db.Text)
    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f"<ProductionAlert {self.date} - {self.alert_type}>"