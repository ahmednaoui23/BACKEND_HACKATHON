from flask import Blueprint, jsonify, request
from services.quality_service import (
    get_kpi_qualite_today,
    get_kpi_qualite_machine,
    get_kpi_qualite_atelier,
    get_kpi_qualite_global,
    get_kpi_qualite_series,
    get_quality_alerts,
    mark_quality_alert_read
)

quality_bp = Blueprint("quality", __name__)

@quality_bp.route("/quality/kpis/today", methods=["GET"])
def kpi_qualite_today():
    data = get_kpi_qualite_today()
    return jsonify(data)

@quality_bp.route("/quality/kpis/machine/<machine_id>", methods=["GET"])
def kpi_qualite_machine(machine_id):
    data = get_kpi_qualite_machine(machine_id)
    return jsonify(data)

@quality_bp.route("/quality/kpis/atelier/<atelier>", methods=["GET"])
def kpi_qualite_atelier(atelier):
    data = get_kpi_qualite_atelier(atelier)
    return jsonify(data)

@quality_bp.route("/quality/kpis/global", methods=["GET"])
def kpi_qualite_global():
    data = get_kpi_qualite_global()
    return jsonify(data)

@quality_bp.route("/quality/kpis/series", methods=["GET"])
def kpi_qualite_series():
    machine_id = request.args.get("machine_id", "ALL")
    data = get_kpi_qualite_series(machine_id)
    return jsonify(data)

@quality_bp.route("/quality/alerts", methods=["GET"])
def quality_alerts():
    severity = request.args.get("severity")
    data = get_quality_alerts(severity)
    return jsonify(data)

@quality_bp.route("/quality/alerts/<int:alert_id>/read", methods=["PATCH"])
def read_quality_alert(alert_id):
    data = mark_quality_alert_read(alert_id)
    return jsonify(data)