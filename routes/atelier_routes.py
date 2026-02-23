from flask import Blueprint, jsonify
from services.atelier_service import (
    get_rendement_atelier,
    get_top10_atelier,
    get_flop10_atelier
)

atelier_bp = Blueprint("atelier", __name__)

@atelier_bp.route("/rendement/atelier/<nom>", methods=["GET"])
def rendement_atelier(nom):
    data = get_rendement_atelier(nom)
    return jsonify(data)

@atelier_bp.route("/rendement/atelier/<nom>/top10", methods=["GET"])
def top10_atelier(nom):
    data = get_top10_atelier(nom)
    return jsonify(data)

@atelier_bp.route("/rendement/atelier/<nom>/flop10", methods=["GET"])
def flop10_atelier(nom):
    data = get_flop10_atelier(nom)
    return jsonify(data)