# 🏭 API Rendement Usine Textile

API REST développée avec **Python Flask + SQLAlchemy + MySQL** pour calculer et visualiser le rendement complet d'une usine textile — employés, machines, ateliers et usine globale.

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

## 🔌 Endpoints API

### 👷 Employé
| Méthode | URL | Description |
|---|---|---|
| GET | `/rendement/employe/{id}` | Fiche complète rendement employé |
| GET | `/rendement/employe/{id}/historique` | Historique et évolution |

### ⚙️ Machine
| Méthode | URL | Description |
|---|---|---|
| GET | `/rendement/machine/{id}` | Fiche complète rendement machine |

### 🏢 Atelier
| Méthode | URL | Description |
|---|---|---|
| GET | `/rendement/atelier/{nom}` | Rendement global de l'atelier |
| GET | `/rendement/atelier/{nom}/top10` | Top 10 employés performers |
| GET | `/rendement/atelier/{nom}/flop10` | Flop 10 employés à surveiller |

### 📋 Tâches
| Méthode | URL | Description |
|---|---|---|
| GET | `/rendement/taches` | Stats globales des tâches |

### 🏭 Usine
| Méthode | URL | Description |
|---|---|---|
| GET | `/rendement/usine` | Rendement global de l'usine |

### 🌍 Global
| Méthode | URL | Description |
|---|---|---|
| GET | `/rendement/global` | Tout en une seule réponse |

---

## 📊 Indicateurs calculés

### Employé (12 indicateurs)
**Normaux**
- Taux de présence
- Taux de ponctualité
- Score rendement global
- Nombre de tâches complétées
- Taux d'anomalies générées
- Classement dans l'atelier
- Meilleur shift

**Cachés**
- Indice d'épuisement progressif
- Indice burnout
- Rendement résiduel après congé
- Rendement nocturne ajusté
- Évolution sur 6 mois

### Machine (9 indicateurs)
**Normaux**
- Taux de disponibilité
- Taux d'utilisation
- OEE (Overall Equipment Effectiveness)
- Classement dans l'atelier
- Top 5 employés utilisateurs

**Cachés**
- Indice de dégradation
- Rendement énergétique
- Fréquence de cycle optimal
- Indice d'impact panne

### Atelier (10 indicateurs)
**Normaux**
- Rendement moyen atelier
- Taux de complétion des tâches
- Taux d'anomalies
- Machines actives / en panne
- Meilleur shift
- Benchmark vs autres ateliers

**Cachés**
- Équilibre de charge
- Indice de chaleur productive
- Vitesse de récupération après incident
- Vitesse de montée en régime

### Tâches (9 indicateurs)
**Normaux**
- Taux de complétion global
- Taux d'anomalies global
- Efficacité temps réel
- Rendement par produit textile

**Cachés**
- Taux de première réussite
- Rendement par shift
- Rendement par tranche horaire
- Taux de répétition inutile
- Débit horaire

### Usine (8 indicateurs)
**Normaux**
- Rendement global usine
- Taux de gaspillage de capacité
- Taux de complétion global
- Meilleur atelier
- Atelier le plus dégradé
- Rendement par atelier

**Cachés**
- Rendement de résilience
- Tendance sur 6 mois

---

## 🛠️ Technologies utilisées

| Technologie | Rôle |
|---|---|
| Python 3 | Langage principal |
| Flask | Framework API REST |
| Flask-CORS | Gestion CORS pour le frontend |
| SQLAlchemy | ORM base de données |
| Flask-SQLAlchemy | Intégration Flask + SQLAlchemy |
| PyMySQL | Connecteur MySQL |
| MySQL Workbench | Gestion base de données |

---

## 🧪 Tester avec Postman

1. Ouvrir Postman
2. Choisir méthode **GET**
3. Taper l'URL ex: `http://127.0.0.1:5000/rendement/usine`
4. Cliquer **Send**
5. Le résultat JSON s'affiche

---

## 📝 Notes

- Remplacer `{id}` par un vrai `employee_id` de la table ex: `E001`
- Remplacer `{nom}` par un vrai nom d'atelier ex: `Coupe`
- Les endpoints `/rendement/taches` et `/rendement/global` peuvent être lents sur de grandes bases de données