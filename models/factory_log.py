from config import db

class FactoryLog(db.Model):
    __tablename__ = "factory_logs"

    log_id = db.Column(db.Text, primary_key=True)
    employee_id = db.Column(db.Text)
    machine_id = db.Column(db.Text)
    task_name = db.Column(db.Text)
    tag_event_start = db.Column(db.Text)
    tag_event_end = db.Column(db.Text)
    task_duration_min = db.Column(db.Float)
    shift = db.Column(db.Text)
    product = db.Column(db.Text)
    task_status = db.Column(db.Text)
    anomaly_flag = db.Column(db.Integer)