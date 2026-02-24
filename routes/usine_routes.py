from flask import Blueprint, jsonify
from services.usine_service import (
    get_rendement_usine,
    get_pouls_usine,
    get_carte_risques,
    get_rapport_mensuel
)
usine_bp = Blueprint("usine", __name__)
# déjà existant
@usine_bp.route("/rendement/usine", methods=["GET"])
def rendement_usine():
    data = get_rendement_usine()
    return jsonify(data)

# NOUVEAU
@usine_bp.route("/usine/pouls", methods=["GET"])
def pouls_usine():
    data = get_pouls_usine()
    return jsonify(data)

@usine_bp.route("/usine/risques", methods=["GET"])
def carte_risques():
    data = get_carte_risques()
    return jsonify(data)

@usine_bp.route("/usine/rapport", methods=["GET"])
def rapport_mensuel():
    data = get_rapport_mensuel()
    return jsonify(data)