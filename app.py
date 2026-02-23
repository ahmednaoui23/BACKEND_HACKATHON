from flask import Flask
from flask_cors import CORS
from config import db, Config

from routes.employe_routes import employe_bp
from routes.machine_routes import machine_bp
from routes.atelier_routes import atelier_bp
from routes.taches_routes import taches_bp
from routes.usine_routes import usine_bp
from routes.global_routes import global_bp
app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(global_bp)
db.init_app(app)
CORS(app)

app.register_blueprint(employe_bp)
app.register_blueprint(machine_bp)
app.register_blueprint(atelier_bp)
app.register_blueprint(taches_bp)
app.register_blueprint(usine_bp)

if __name__ == "__main__":
    app.run(debug=True)