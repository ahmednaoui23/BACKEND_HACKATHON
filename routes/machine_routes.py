from flask import Blueprint, jsonify, request
from services.machine_service import (
    # CRUD
    get_all_machines,
    get_machine_by_id,
    create_machine,
    update_machine,
    delete_machine,
    # KPI
    get_kpi_machines_today,
    get_kpi_machine_by_id,
    get_kpi_by_atelier,
    get_kpi_machines_aggregated,
    get_kpi_machine_series,
    get_machine_alerts,
    mark_machine_alert_read
)

machine_bp = Blueprint("machine", __name__)


# ============================================================
# CRUD
# ============================================================
@machine_bp.route("/machines", methods=["GET"])
def all_machines():
    atelier      = request.args.get("atelier")
    type_machine = request.args.get("type_machine")
    etat         = request.args.get("etat")
    data = get_all_machines(atelier, type_machine, etat)
    return jsonify(data)


@machine_bp.route("/machines/<machine_id>", methods=["GET"])
def machine_by_id(machine_id):
    data = get_machine_by_id(machine_id)
    return jsonify(data)


@machine_bp.route("/machines", methods=["POST"])
def add_machine():
    body = request.get_json()
    data = create_machine(body)
    return jsonify(data), 201


@machine_bp.route("/machines/<machine_id>", methods=["PUT"])
def edit_machine(machine_id):
    body = request.get_json()
    data = update_machine(machine_id, body)
    return jsonify(data)


@machine_bp.route("/machines/<machine_id>", methods=["DELETE"])
def remove_machine(machine_id):
    data = delete_machine(machine_id)
    return jsonify(data)


# ============================================================
# KPI
# ============================================================

# Toutes les machines + KPI
@machine_bp.route("/machine/kpis/today", methods=["GET"])
def kpi_machines_today():
    data = get_kpi_machines_today()
    return jsonify(data)


# 1 machine précise par ID
@machine_bp.route("/machine/kpis/<machine_id>", methods=["GET"])
def kpi_machine_by_id(machine_id):
    data = get_kpi_machine_by_id(machine_id)
    return jsonify(data)


# Toutes les machines d'un atelier
@machine_bp.route("/machine/kpis/atelier/<atelier>", methods=["GET"])
def kpi_by_atelier(atelier):
    data = get_kpi_by_atelier(atelier)
    return jsonify(data)


# KPI agrégé depuis daily_machine_kpi
@machine_bp.route("/machine/kpis/aggregated", methods=["GET"])
def kpi_machines_aggregated():
    data = get_kpi_machines_aggregated()
    return jsonify(data)


# Séries temporelles pour 1 machine
@machine_bp.route("/machine/kpis/series/<machine_id>", methods=["GET"])
def kpi_machine_series(machine_id):
    data = get_kpi_machine_series(machine_id)
    return jsonify(data)


# Alertes machines actives
@machine_bp.route("/machine/alerts", methods=["GET"])
def machine_alerts():
    severity = request.args.get("severity")
    data = get_machine_alerts(severity)
    return jsonify(data)


# Marquer alerte lue
@machine_bp.route("/machine/alerts/<int:alert_id>/read", methods=["PATCH"])
def read_machine_alert(alert_id):
    data = mark_machine_alert_read(alert_id)
    return jsonify(data)