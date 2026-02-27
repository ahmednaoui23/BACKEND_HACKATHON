from config import db

class HrAlert(db.Model):
    __tablename__ = "hr_alerts"

    id          = db.Column(db.Integer, primary_key=True)
    date        = db.Column(db.Date, nullable=False)
    employee_id = db.Column(db.Text, nullable=True)
    shift       = db.Column(db.Text)
    alert_type  = db.Column(db.Text)
    severity    = db.Column(db.Text)
    message     = db.Column(db.Text)
    is_read     = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f"<HrAlert {self.date} - {self.alert_type} - {self.severity}>"