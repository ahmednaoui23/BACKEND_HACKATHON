from flask import Blueprint, jsonify, request
from services.production_service import (
    get_kpi_production_today,
    get_kpi_production_by_shift,
    get_kpi_production_by_atelier,
    get_kpi_production_aggregated,
    get_kpi_production_series,
    get_production_alerts,
    mark_production_alert_read
)

production_bp = Blueprint("production", __name__)

@production_bp.route("/production/kpis/today", methods=["GET"])
def kpi_production_today():
    data = get_kpi_production_today()
    return jsonify(data)

@production_bp.route("/production/kpis/shift/<shift>", methods=["GET"])
def kpi_production_by_shift(shift):
    data = get_kpi_production_by_shift(shift)
    return jsonify(data)

@production_bp.route("/production/kpis/atelier/<atelier>", methods=["GET"])
def kpi_production_by_atelier(atelier):
    data = get_kpi_production_by_atelier(atelier)
    return jsonify(data)

@production_bp.route("/production/kpis/aggregated", methods=["GET"])
def kpi_production_aggregated():
    data = get_kpi_production_aggregated()
    return jsonify(data)

@production_bp.route("/production/kpis/series", methods=["GET"])
def kpi_production_series():
    shift   = request.args.get("shift", "ALL")
    atelier = request.args.get("atelier", "ALL")
    data    = get_kpi_production_series(shift, atelier)
    return jsonify(data)

@production_bp.route("/production/alerts", methods=["GET"])
def production_alerts():
    severity = request.args.get("severity")
    data = get_production_alerts(severity)
    return jsonify(data)

@production_bp.route("/production/alerts/<int:alert_id>/read", methods=["PATCH"])
def read_production_alert(alert_id):
    data = mark_production_alert_read(alert_id)
    return jsonify(data)