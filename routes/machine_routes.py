from flask import Blueprint, jsonify, request
from services.machine_service import (
    get_rendement_machine,
    get_all_machines,
    get_machine_by_id,
    create_machine,
    update_machine,
    delete_machine
)

machine_bp = Blueprint("machine", __name__)

# déjà existant
@machine_bp.route("/rendement/machine/<machine_id>", methods=["GET"])
def rendement_machine(machine_id):
    data = get_rendement_machine(machine_id)
    return jsonify(data)

# NOUVEAU
@machine_bp.route("/machines", methods=["GET"])
def all_machines():
    atelier = request.args.get("atelier")
    etat = request.args.get("etat")
    data = get_all_machines(atelier, etat)
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