from config import db

class Machine(db.Model):
    __tablename__ = "machines_realiste_textile"

    machine_id = db.Column(db.Text, primary_key=True)
    nom_machine = db.Column(db.Text)
    type_machine = db.Column(db.Text)
    atelier = db.Column(db.Text)
    tache = db.Column(db.Text)
    unite_production = db.Column(db.Text)
    capacite = db.Column(db.Integer)
    temps_par_unite_min = db.Column(db.Float)
    temps_total_tache_min = db.Column(db.Integer)
    operateurs_requis = db.Column(db.Integer)
    pannes_mois = db.Column(db.Integer)
    etat_machine = db.Column(db.Text)
    annee_installation = db.Column(db.Integer)
    marque = db.Column(db.Text)
    consommation_energie = db.Column(db.Text)
    rendement_machine = db.Column(db.Float)