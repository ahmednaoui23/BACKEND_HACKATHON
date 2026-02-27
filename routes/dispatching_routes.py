from flask import Blueprint, jsonify, request
from services.dispatching_service import run_dispatching , run_dispatching_hungarian, worst_real_dispatching

dispatching_bp = Blueprint("dispatching", __name__)

@dispatching_bp.route("/dispatching", methods=["GET"])
def dispatching():
    data = run_dispatching()
    return jsonify(data)

@dispatching_bp.route("/dispatching/hungarian", methods=["GET"])
def dispatching_hungarian():
    data = run_dispatching_hungarian()
    return jsonify(data)
@dispatching_bp.route("/worst_real_dispatching", methods=["GET"])
def get_worst_real_dispatching():
    """
    Endpoint pour récupérer le pire employé par machine/product
    Paramètre URL : ?day=YYYY-MM-DD
    """
    day = request.args.get("day")
    if not day:
        return jsonify({"error": "Veuillez fournir le paramètre day au format YYYY-MM-DD"}), 400

    results = worst_real_dispatching(day)
    return jsonify(results)