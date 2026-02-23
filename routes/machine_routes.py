from flask import Blueprint, jsonify
from services.machine_service import get_rendement_machine

machine_bp = Blueprint("machine", __name__)

@machine_bp.route("/rendement/machine/<machine_id>", methods=["GET"])
def rendement_machine(machine_id):
    data = get_rendement_machine(machine_id)
    return jsonify(data)