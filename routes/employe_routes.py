from flask import Blueprint, jsonify, request
from services.employe_service import (
    # CRUD existant
    get_all_employes,
    get_employe_by_id,
    create_employe,
    update_employe,
    delete_employe,
    get_rendement_employe,
    get_historique_employe,
    # KPI nouveaux
    get_kpi_employes_today,
    get_kpi_employe_by_id,
    get_kpi_by_shift,
    get_kpi_by_departement,
    get_kpi_shift_today,
    get_kpi_hr_series,
    get_hr_alerts,
    mark_alert_read
)

employe_bp = Blueprint("employe", __name__)


# ============================================================
# CRUD EXISTANT — inchangé
# ============================================================

@employe_bp.route("/employes", methods=["GET"])
def all_employes():
    departement = request.args.get("departement")
    shift       = request.args.get("shift")
    poste       = request.args.get("poste")
    data = get_all_employes(departement, shift, poste)
    return jsonify(data)


@employe_bp.route("/employes/<employee_id>", methods=["GET"])
def employe_by_id(employee_id):
    data = get_employe_by_id(employee_id)
    return jsonify(data)


@employe_bp.route("/employes", methods=["POST"])
def add_employe():
    body = request.get_json()
    data = create_employe(body)
    return jsonify(data), 201


@employe_bp.route("/employes/<employee_id>", methods=["PUT"])
def edit_employe(employee_id):
    body = request.get_json()
    data = update_employe(employee_id, body)
    return jsonify(data)


@employe_bp.route("/employes/<employee_id>", methods=["DELETE"])
def remove_employe(employee_id):
    data = delete_employe(employee_id)
    return jsonify(data)


@employe_bp.route("/rendement/employe/<employee_id>", methods=["GET"])
def rendement_employe(employee_id):
    data = get_rendement_employe(employee_id)
    return jsonify(data)


@employe_bp.route("/rendement/employe/<employee_id>/historique", methods=["GET"])
def historique_employe(employee_id):
    data = get_historique_employe(employee_id)
    return jsonify(data)


# ============================================================
# KPI NOUVEAUX
# ============================================================

# Tous les employés
@employe_bp.route("/hr/kpis/employes/today", methods=["GET"])
def kpi_employes_today():
    data = get_kpi_employes_today()
    return jsonify(data)


# 1 employé précis par ID
@employe_bp.route("/hr/kpis/employe/<employee_id>", methods=["GET"])
def kpi_employe_by_id(employee_id):
    data = get_kpi_employe_by_id(employee_id)
    return jsonify(data)


# Tous les employés d'un shift
@employe_bp.route("/hr/kpis/shift/<shift>", methods=["GET"])
def kpi_by_shift(shift):
    data = get_kpi_by_shift(shift)
    return jsonify(data)


# Tous les employés d'un département / atelier
@employe_bp.route("/hr/kpis/departement/<departement>", methods=["GET"])
def kpi_by_departement(departement):
    data = get_kpi_by_departement(departement)
    return jsonify(data)


# KPI agrégé par shift depuis daily_hr_kpi
@employe_bp.route("/hr/kpis/today", methods=["GET"])
def kpi_shift_today():
    data = get_kpi_shift_today()
    return jsonify(data)


# Séries temporelles mois précédent vs mois actuel
# GET /hr/kpis/series?shift=ALL
@employe_bp.route("/hr/kpis/series", methods=["GET"])
def kpi_hr_series():
    shift = request.args.get("shift", "ALL")
    data  = get_kpi_hr_series(shift)
    return jsonify(data)


# Alertes RH actives
# GET /hr/alerts
# GET /hr/alerts?severity=critical
@employe_bp.route("/hr/alerts", methods=["GET"])
def hr_alerts():
    severity = request.args.get("severity")
    data = get_hr_alerts(severity)
    return jsonify(data)


# Marquer alerte comme lue
@employe_bp.route("/hr/alerts/<int:alert_id>/read", methods=["PATCH"])
def read_alert(alert_id):
    data = mark_alert_read(alert_id)
    return jsonify(data)


