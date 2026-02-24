from flask import Blueprint, jsonify, request
from services.employe_service import (
    get_rendement_employe,
    get_historique_employe,
    get_all_employes,
    get_employe_by_id,
    create_employe,
    update_employe,
    delete_employe
)

employe_bp = Blueprint("employe", __name__)

# déjà existant
@employe_bp.route("/rendement/employe/<employee_id>", methods=["GET"])
def rendement_employe(employee_id):
    data = get_rendement_employe(employee_id)
    return jsonify(data)

@employe_bp.route("/rendement/employe/<employee_id>/historique", methods=["GET"])
def historique_employe(employee_id):
    data = get_historique_employe(employee_id)
    return jsonify(data)

# NOUVEAU
@employe_bp.route("/employes", methods=["GET"])
def all_employes():
    departement = request.args.get("departement")
    shift = request.args.get("shift")
    poste = request.args.get("poste")
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