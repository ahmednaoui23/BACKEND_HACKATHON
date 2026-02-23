from flask import Blueprint, jsonify
from services.employe_service import (
    get_rendement_employe,
    get_historique_employe
)

employe_bp = Blueprint("employe", __name__)

@employe_bp.route("/rendement/employe/<employee_id>", methods=["GET"])
def rendement_employe(employee_id):
    data = get_rendement_employe(employee_id)
    return jsonify(data)

@employe_bp.route("/rendement/employe/<employee_id>/historique", methods=["GET"])
def historique_employe(employee_id):
    data = get_historique_employe(employee_id)
    return jsonify(data)