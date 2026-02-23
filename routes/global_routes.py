from flask import Blueprint, jsonify
from services.global_service import get_rendement_global

global_bp = Blueprint("global", __name__)

@global_bp.route("/rendement/global", methods=["GET"])
def rendement_global():
    data = get_rendement_global()
    return jsonify(data)