from flask import Blueprint, jsonify
from services.taches_service import get_rendement_taches

taches_bp = Blueprint("taches", __name__)

@taches_bp.route("/rendement/taches", methods=["GET"])
def rendement_taches():
    data = get_rendement_taches()
    return jsonify(data)