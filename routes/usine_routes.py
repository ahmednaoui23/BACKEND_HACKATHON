from flask import Blueprint, jsonify
from services.usine_service import get_rendement_usine

usine_bp = Blueprint("usine", __name__)

@usine_bp.route("/rendement/usine", methods=["GET"])
def rendement_usine():
    data = get_rendement_usine()
    return jsonify(data)