from flask import Blueprint, jsonify, request
from config import db
from services.atelier_service import (
    get_rendement_atelier,
    get_top10_atelier,
    get_flop10_atelier,
    get_adn_atelier,
    comparer_ateliers
)

atelier_bp = Blueprint("atelier", __name__)

# RENDEMENT
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

# NOUVEAU
@atelier_bp.route("/ateliers", methods=["GET"])
def all_ateliers():
    from models.machine import Machine
    ateliers = db.session.query(Machine.atelier).distinct().all()
    return jsonify([a[0] for a in ateliers])

@atelier_bp.route("/ateliers/<nom>/employes", methods=["GET"])
def employes_atelier(nom):
    from services.employe_service import get_all_employes
    data = get_all_employes(departement=nom)
    return jsonify(data)

@atelier_bp.route("/ateliers/<nom>/machines", methods=["GET"])
def machines_atelier(nom):
    from services.machine_service import get_all_machines
    data = get_all_machines(atelier=nom)
    return jsonify(data)

@atelier_bp.route("/ateliers/<nom>/adn", methods=["GET"])
def adn_atelier(nom):
    data = get_adn_atelier(nom)
    return jsonify(data)

@atelier_bp.route("/ateliers/comparer", methods=["GET"])
def comparer():
    a = request.args.get("a")
    b = request.args.get("b")
    data = comparer_ateliers(a, b)
    return jsonify(data)