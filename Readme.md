# 🏭 API Rendement Usine Textile

API REST développée avec **Python Flask + SQLAlchemy + MySQL** pour gérer et visualiser le rendement complet d'une usine textile — employés, machines, ateliers et usine globale.

---

## 📁 Structure du projet

```
projet_usine/
├── requirements.txt
├── config.py
├── app.py
├── models/
│   ├── __init__.py
│   ├── employee.py
│   ├── machine.py
│   └── factory_log.py
├── routes/
│   ├── __init__.py
│   ├── employe_routes.py
│   ├── machine_routes.py
│   ├── atelier_routes.py
│   ├── taches_routes.py
│   ├── usine_routes.py
│   └── global_routes.py
└── services/
    ├── __init__.py
    ├── employe_service.py
    ├── machine_service.py
    ├── atelier_service.py
    ├── taches_service.py
    ├── usine_service.py
    └── global_service.py
```

---

## 🗄️ Base de données

3 tables MySQL :

| Table | Description |
|---|---|
| `employee` | Données RH, performance, présence, rendement |
| `machines_realiste_textile` | Données machines, pannes, OEE, énergie |
| `factory_logs` | Logs de tâches en temps réel par machine et employé |

---

## ⚙️ Installation

**1 — Créer l'environnement virtuel**
```bash
python -m venv venv
```

**2 — Activer l'environnement virtuel**
```bash
# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

**3 — Installer les dépendances**
```bash
pip install -r requirements.txt
```

**4 — Configurer la base de données**

Dans `config.py`, remplacer :
```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:tonmotdepasse@localhost/nom_ta_base"
```

**5 — Lancer l'API**
```bash
python app.py
```

> L'API tourne sur `http://127.0.0.1:5000`

---

## 🔌 Endpoints API — 27 endpoints

### 👷 Employés — CRUD
| Méthode | URL | Description |
|---|---|---|
| GET | `/employes` | Liste tous les employés |
| GET | `/employes?departement=Coupe` | Filtrer par département |
| GET | `/employes?shift=nuit` | Filtrer par shift |
| GET | `/employes?poste=Opérateur` | Filtrer par poste |
| GET | `/employes/{id}` | Profil complet employé |
| POST | `/employes` | Créer un employé |
| PUT | `/employes/{id}` | Modifier un employé |
| DELETE | `/employes/{id}` | Supprimer un employé |

### ⚙️ Machines — CRUD
| Méthode | URL | Description |
|---|---|---|
| GET | `/machines` | Liste toutes les machines |
| GET | `/machines?atelier=Coupe` | Filtrer par atelier |
| GET | `/machines?etat=en panne` | Filtrer par état |
| GET | `/machines/{id}` | Détail complet machine |
| POST | `/machines` | Créer une machine |
| PUT | `/machines/{id}` | Modifier une machine |
| DELETE | `/machines/{id}` | Supprimer une machine |

### 🏢 Ateliers
| Méthode | URL | Description |
|---|---|---|
| GET | `/ateliers` | Liste tous les ateliers |
| GET | `/ateliers/{nom}/employes` | Employés d'un atelier |
| GET | `/ateliers/{nom}/machines` | Machines d'un atelier |
| GET | `/ateliers/{nom}/adn` | ADN complet atelier |
| GET | `/ateliers/comparer?a=X&b=Y` | Comparer 2 ateliers |

### 🏭 Usine
| Méthode | URL | Description |
|---|---|---|
| GET | `/usine/pouls` | Snapshot temps réel usine |
| GET | `/usine/risques` | Carte des risques |
| GET | `/usine/rapport` | Rapport mensuel complet |

### 📊 Rendement
| Méthode | URL | Description |
|---|---|---|
| GET | `/rendement/employe/{id}` | Fiche rendement employé |
| GET | `/rendement/employe/{id}/historique` | Historique et évolution |
| GET | `/rendement/machine/{id}` | Fiche rendement machine |
| GET | `/rendement/atelier/{nom}` | Rendement global atelier |
| GET | `/rendement/atelier/{nom}/top10` | Top 10 performers |
| GET | `/rendement/atelier/{nom}/flop10` | Flop 10 à surveiller |
| GET | `/rendement/taches` | Stats globales tâches |
| GET | `/rendement/usine` | Rendement global usine |
| GET | `/rendement/global` | Tout en une seule réponse |

---

## 📊 Indicateurs de rendement calculés (48 indicateurs)

### Employé (12)
**Normaux** — Taux de présence, Taux de ponctualité, Score rendement global, Tâches complétées, Taux d'anomalies, Classement atelier, Meilleur shift

**Cachés** — Indice d'épuisement, Indice burnout, Rendement après congé, Rendement nocturne ajusté, Évolution 6 mois

### Machine (9)
**Normaux** — Taux de disponibilité, Taux d'utilisation, OEE, Classement atelier, Top 5 employés

**Cachés** — Indice de dégradation, Rendement énergétique, Fréquence cycle optimal, Indice impact panne

### Atelier (10)
**Normaux** — Rendement moyen, Taux complétion, Taux anomalies, Machines actives/en panne, Meilleur shift, Benchmark

**Cachés** — Équilibre de charge, Indice chaleur productive, Vitesse récupération, Vitesse montée en régime

### Tâches (9)
**Normaux** — Taux complétion global, Taux anomalies, Efficacité temps réel, Rendement par produit

**Cachés** — Taux première réussite, Rendement par shift, Rendement par tranche horaire, Taux répétition inutile, Débit horaire

### Usine (8)
**Normaux** — Rendement global, Taux gaspillage, Taux complétion, Meilleur atelier, Atelier dégradé, Rendement par atelier

**Cachés** — Rendement résilience, Tendance 6 mois

---

## 🧪 Tester avec Postman

**GET simple**
```
GET http://127.0.0.1:5000/employes
GET http://127.0.0.1:5000/usine/pouls
GET http://127.0.0.1:5000/rendement/usine
```

**POST / PUT — Body → raw → JSON**
```json
{
  "employee_id": "E001",
  "nom": "Ben Ali",
  "prenom": "Ahmed",
  "poste": "Opérateur",
  "departement": "Coupe",
  "shift_travail": "matin"
}
```

---

## 🛠️ Technologies utilisées

| Technologie | Rôle |
|---|---|
| Python 3 | Langage principal |
| Flask | Framework API REST |
| Flask-CORS | Gestion CORS frontend |
| SQLAlchemy | ORM base de données |
| Flask-SQLAlchemy | Intégration Flask + SQLAlchemy |
| PyMySQL | Connecteur MySQL |
| MySQL Workbench | Gestion base de données |

---

## 📝 Notes

- Remplacer `{id}` par un vrai `employee_id` ex: `E001`
- Remplacer `{nom}` par un vrai nom d'atelier ex: `Coupe`
- Les endpoints `/rendement/taches` et `/rendement/global` peuvent être lents sur de grandes bases de données