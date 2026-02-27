from config import db

class MachineAlert(db.Model):
    __tablename__ = "machine_alerts"

    id         = db.Column(db.Integer, primary_key=True)
    date       = db.Column(db.Date, nullable=False)
    machine_id = db.Column(db.Text)
    alert_type = db.Column(db.Text)
    severity   = db.Column(db.Text)
    message    = db.Column(db.Text)
    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f"<MachineAlert {self.date} - {self.alert_type} - {self.severity}>"