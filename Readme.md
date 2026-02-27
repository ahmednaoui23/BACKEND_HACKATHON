# 🏭 API Rendement Usine Textile

API REST développée avec **Python Flask + SQLAlchemy + MySQL** pour gérer et visualiser le rendement complet d'une usine textile — employés, machines, ateliers, qualité et KPI temps réel.

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
│   ├── factory_log.py
│   ├── daily_hr_kpi.py          ← NOUVEAU
│   ├── hr_alert.py               ← NOUVEAU
│   ├── daily_machine_kpi.py      ← NOUVEAU
│   ├── machine_alert.py          ← NOUVEAU
│   ├── daily_quality_kpi.py      ← NOUVEAU
│   └── quality_alert.py          ← NOUVEAU
├── routes/
│   ├── __init__.py
│   ├── employe_routes.py
│   ├── machine_routes.py
│   ├── atelier_routes.py
│   ├── taches_routes.py
│   ├── usine_routes.py
│   ├── global_routes.py
│   └── quality_routes.py         ← NOUVEAU
├── services/
│   ├── __init__.py
│   ├── employe_service.py
│   ├── machine_service.py
│   ├── atelier_service.py
│   ├── taches_service.py
│   ├── usine_service.py
│   ├── global_service.py
│   └── quality_service.py        ← NOUVEAU
└── scheduler/
    ├── __init__.py
    ├── hr_calculator.py           ← NOUVEAU
    ├── hr_scheduler.py            ← NOUVEAU
    ├── machine_calculator.py      ← NOUVEAU
    ├── machine_scheduler.py       ← NOUVEAU
    ├── quality_calculator.py      ← NOUVEAU
    └── quality_scheduler.py       ← NOUVEAU
```

---

## 🗄️ Base de données

### Tables existantes

| Table | Description |
|---|---|
| `employee` | Données RH, performance, présence, rendement, risques |
| `machines_realiste_textile` | Données machines, pannes, OEE, énergie, rendement |
| `factory_logs` | Logs de tâches en temps réel par machine et employé |

### Tables KPI dédiées (nouvelles)

| Table | Description | Fréquence calcul |
|---|---|---|
| `daily_hr_kpi` | KPI RH agrégés par shift et par jour | Toutes les 15 min |
| `hr_alerts` | Alertes RH automatiques (fatigue, absentéisme, rotation) | Toutes les 15 min |
| `daily_machine_kpi` | KPI machines par jour (MTBF, MTTR, disponibilité) | Toutes les 15 min |
| `machine_alerts` | Alertes machines (pannes, anomalies, sous-utilisation) | Toutes les 15 min |
| `daily_quality_kpi` | KPI qualité par machine et global usine | Toutes les 15 min |
| `quality_alerts` | Alertes qualité (anomalies, rejets, DPMO) | Toutes les 15 min |

---

## ⚙️ Installation

### 1 — Créer l'environnement virtuel
```bash
python -m venv venv
```

### 2 — Activer l'environnement virtuel
```bash
# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3 — Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4 — Configurer la base de données
Dans `config.py` :
```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:tonmotdepasse@localhost:3306/nom_ta_base"
```

### 5 — Lancer l'API
```bash
python app.py
```

Les tables KPI sont créées automatiquement au démarrage. Le scheduler démarre immédiatement et calcule les KPI toutes les 15 minutes.

L'API tourne sur **http://127.0.0.1:5000**

---

## 🔌 Endpoints API — 54 endpoints

### 👷 Employés — CRUD

| Méthode | URL | Description |
|---|---|---|
| GET | `/employes` | Liste tous les employés |
| GET | `/employes?departement=Coupe` | Filtrer par département |
| GET | `/employes?shift=Matin` | Filtrer par shift |
| GET | `/employes?poste=Opérateur` | Filtrer par poste |
| GET | `/employes/{id}` | Profil complet employé |
| POST | `/employes` | Créer un employé |
| PUT | `/employes/{id}` | Modifier un employé |
| DELETE | `/employes/{id}` | Supprimer un employé |
| GET | `/rendement/employe/{id}` | Fiche rendement employé |
| GET | `/rendement/employe/{id}/historique` | Historique et évolution |

### 👷 Employés — KPI temps réel (NOUVEAU)

| Méthode | URL | Description |
|---|---|---|
| GET | `/hr/kpis/employes/today` | KPI de tous les employés |
| GET | `/hr/kpis/employe/{id}` | KPI d'un employé précis |
| GET | `/hr/kpis/shift/{shift}` | KPI de tous les employés d'un shift |
| GET | `/hr/kpis/departement/{departement}` | KPI de tous les employés d'un atelier |
| GET | `/hr/kpis/today` | KPI agrégés par shift depuis daily_hr_kpi |
| GET | `/hr/kpis/series?shift=ALL` | Courbes mois précédent vs mois actuel |
| GET | `/hr/alerts` | Alertes RH actives non lues |
| GET | `/hr/alerts?severity=critical` | Alertes critiques uniquement |
| PATCH | `/hr/alerts/{id}/read` | Marquer une alerte comme lue |

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
| GET | `/rendement/machine/{id}` | Fiche rendement machine |

### ⚙️ Machines — KPI temps réel (NOUVEAU)

| Méthode | URL | Description |
|---|---|---|
| GET | `/machine/kpis/today` | KPI de toutes les machines |
| GET | `/machine/kpis/{machine_id}` | KPI d'une machine précise |
| GET | `/machine/kpis/atelier/{atelier}` | KPI des machines d'un atelier |
| GET | `/machine/kpis/aggregated` | KPI agrégés depuis daily_machine_kpi |
| GET | `/machine/kpis/series/{machine_id}` | Courbes mois précédent vs mois actuel |
| GET | `/machine/alerts` | Alertes machines actives non lues |
| GET | `/machine/alerts?severity=critical` | Alertes critiques uniquement |
| PATCH | `/machine/alerts/{id}/read` | Marquer une alerte comme lue |

### 📊 Qualité — KPI temps réel (NOUVEAU)

| Méthode | URL | Description |
|---|---|---|
| GET | `/quality/kpis/today` | KPI qualité de toutes les machines |
| GET | `/quality/kpis/machine/{machine_id}` | KPI qualité d'une machine précise |
| GET | `/quality/kpis/atelier/{atelier}` | KPI qualité d'un atelier |
| GET | `/quality/kpis/global` | KPI qualité global usine entière |
| GET | `/quality/kpis/series?machine_id=ALL` | Courbes mois précédent vs mois actuel |
| GET | `/quality/alerts` | Alertes qualité actives non lues |
| GET | `/quality/alerts?severity=critical` | Alertes critiques uniquement |
| PATCH | `/quality/alerts/{id}/read` | Marquer une alerte comme lue |

### 🏢 Ateliers

| Méthode | URL | Description |
|---|---|---|
| GET | `/ateliers` | Liste tous les ateliers |
| GET | `/ateliers/{nom}/employes` | Employés d'un atelier |
| GET | `/ateliers/{nom}/machines` | Machines d'un atelier |
| GET | `/ateliers/{nom}/adn` | ADN complet atelier |
| GET | `/rendement/atelier/{nom}` | Rendement global atelier |
| GET | `/rendement/atelier/{nom}/top10` | Top 10 performers |
| GET | `/rendement/atelier/{nom}/flop10` | Flop 10 à surveiller |
| GET | `/ateliers/comparer?a=X&b=Y` | Comparer 2 ateliers |

### 🏭 Usine

| Méthode | URL | Description |
|---|---|---|
| GET | `/usine/pouls` | Snapshot temps réel usine |
| GET | `/usine/risques` | Carte des risques |
| GET | `/usine/rapport` | Rapport mensuel complet |
| GET | `/rendement/usine` | Rendement global usine |
| GET | `/rendement/global` | Tout en une seule réponse |

### 📋 Tâches

| Méthode | URL | Description |
|---|---|---|
| GET | `/rendement/taches` | Stats globales tâches |

---

## 🤖 Schedulers — Calcul KPI automatique

```
Toutes les 15 minutes
    ↓
├── hr_calculator      → daily_hr_kpi + hr_alerts
├── machine_calculator → daily_machine_kpi + machine_alerts
└── quality_calculator → daily_quality_kpi + quality_alerts

Chaque nuit
├── 01h00 → consolidation RH
├── 01h30 → consolidation machines
└── 02h00 → consolidation qualité
```

Les tables se remplissent **immédiatement au démarrage** (`next_run_time=datetime.now()`), sans attendre 15 minutes.

---

## 📊 KPI calculés — 60+ indicateurs

### Bloc RH (par employé et par shift)
- Taux de présence, Taux de ponctualité
- Score rendement global `(taux_rendement×0.40 + performance×0.35 + evaluation×0.15 + ponctualité×0.10)`
- Score fatigue `(retards + absences/8 + accidents×5 + maladies×3) / ancienneté`
- Taux complétion tâches, Taux anomalies
- Risque absentéisme, Risque départ
- Indice burnout, Rendement nocturne ajusté

### Bloc Machines (par machine)
- MTBF `(160h / pannes_mois)`
- MTTR `(MTBF × 10%)`
- Disponibilité, Taux d'utilisation
- Taux anomalies, Coût estimé pannes
- OEE `(disponibilité × performance × qualité)`

### Bloc Qualité (par machine et global)
- Taux anomalie, First Pass Quality `(1 - anomaly_rate)`
- Taux de rejet, DPMO `(anomalies / (total × opportunités) × 1,000,000)`
- Stabilité processus

### Bloc Usine
- Rendement global, Taux gaspillage capacité
- Taux complétion global, Taux anomalies global
- Meilleur/pire atelier, Rendement résilience

---

## 🚨 Types d'alertes automatiques

### RH
| Alert Type | Déclencheur |
|---|---|
| `HIGH_ABSENTEEISM` | Taux absentéisme > 15% (critical > 25%) |
| `HIGH_FATIGUE` | Score fatigue > 3.0 (critical > 5.0) |
| `HIGH_ROTATION_RISK` | Nb employés risque départ ≥ 3 |
| `LOW_PRODUCTIVITY` | Productivité moyenne < 60 |
| `ACCIDENT_REPORTED` | accidents_travail > 0 |

### Machines
| Alert Type | Déclencheur |
|---|---|
| `LOW_AVAILABILITY` | Disponibilité < 80% (critical < 60%) |
| `HIGH_ANOMALY_RATE` | Anomalies > 10% (critical > 25%) |
| `LOW_UTILIZATION` | Utilisation < 50% |
| `MACHINE_DOWN` | etat_machine ≠ Opérationnelle |

### Qualité
| Alert Type | Déclencheur |
|---|---|
| `HIGH_ANOMALY_RATE` | Anomalies > 10% (critical > 25%) |
| `HIGH_REJECTION_RATE` | Rejets > 5% (critical > 15%) |
| `LOW_FIRST_PASS_QUALITY` | FPQ < 85% |
| `HIGH_DPMO` | DPMO > 10,000 (critical > 50,000) |

---

## 🧪 Tester avec Postman

### GET simple
```
GET http://127.0.0.1:5000/employes
GET http://127.0.0.1:5000/hr/kpis/today
GET http://127.0.0.1:5000/hr/kpis/employes/today
GET http://127.0.0.1:5000/hr/kpis/shift/Matin
GET http://127.0.0.1:5000/hr/kpis/departement/Couture
GET http://127.0.0.1:5000/hr/alerts
GET http://127.0.0.1:5000/machine/kpis/today
GET http://127.0.0.1:5000/machine/kpis/aggregated
GET http://127.0.0.1:5000/machine/alerts
GET http://127.0.0.1:5000/quality/kpis/global
GET http://127.0.0.1:5000/quality/kpis/today
GET http://127.0.0.1:5000/quality/alerts
GET http://127.0.0.1:5000/usine/pouls
GET http://127.0.0.1:5000/rendement/usine
```

### POST / PUT — Body → raw → JSON
```json
{
  "employee_id": "E001",
  "nom": "Ben Ali",
  "prenom": "Ahmed",
  "poste": "Opérateur",
  "departement": "Coupe",
  "shift_travail": "Matin"
}
```

### PATCH — Marquer alerte lue
```
PATCH http://127.0.0.1:5000/hr/alerts/1/read
PATCH http://127.0.0.1:5000/machine/alerts/1/read
PATCH http://127.0.0.1:5000/quality/alerts/1/read
```

---

## 🔄 Flux temps réel

```
factory_logs reçoit de nouvelles entrées
        ↓
Scheduler se déclenche toutes les 15 min
        ↓
Calcule KPI depuis employee + factory_logs + machines
        ↓
UPSERT dans daily_hr_kpi / daily_machine_kpi / daily_quality_kpi
INSERT dans hr_alerts / machine_alerts / quality_alerts (sans doublons)
        ↓
React poll GET /hr/kpis/today toutes les 30s
        ↓
Courbes mises à jour en live
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
| APScheduler | Scheduler KPI automatique |
| MySQL | Base de données |

---

## 📝 Notes

- Remplacer `{id}` par un vrai `employee_id` ex: `E001`
- Remplacer `{nom}` par un vrai nom d'atelier ex: `Coupe`
- Les shifts valides sont : `Matin`, `Après-midi`, `Nuit`, `ALL`
- L'endpoint `/hr/kpis/today` retourne `vide` si le scheduler n'a pas encore tourné — attendre 1 minute
- Les alertes avec `is_read=true` n'apparaissent plus dans les endpoints alerts
- Le DPMO est calculé avec 5 opportunités par unité (modifiable dans `quality_calculator.py`)
  ## 🗄️ Créer les tables KPI (SQL)

Exécutez ce script dans MySQL Workbench pour créer les 6 tables KPI dédiées :
```sql
-- BLOC RH
CREATE TABLE IF NOT EXISTS daily_hr_kpi (
    id                     INT AUTO_INCREMENT PRIMARY KEY,
    date                   DATE NOT NULL,
    shift                  VARCHAR(50) NOT NULL,
    present_count          INT,
    absent_count           INT,
    absenteeism_rate       DOUBLE,
    avg_productivity       DOUBLE,
    avg_rendement          DOUBLE,
    fatigue_score          DOUBLE,
    rotation_risk_count    INT,
    absenteisme_risk_count INT,
    avg_seniority          DOUBLE,
    computed_at            DATETIME DEFAULT NOW(),
    UNIQUE KEY uq_hr_date_shift (date, shift)
);

CREATE TABLE IF NOT EXISTS hr_alerts (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    date        DATE NOT NULL,
    employee_id VARCHAR(100),
    shift       VARCHAR(50),
    alert_type  VARCHAR(100),
    severity    VARCHAR(20),
    message     TEXT,
    is_read     BOOLEAN DEFAULT FALSE,
    created_at  DATETIME DEFAULT NOW()
);

-- BLOC MACHINES
CREATE TABLE IF NOT EXISTS daily_machine_kpi (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    date             DATE NOT NULL,
    machine_id       VARCHAR(100) NOT NULL,
    mtbf             DOUBLE,
    mttr             DOUBLE,
    availability     DOUBLE,
    utilization_rate DOUBLE,
    anomaly_rate     DOUBLE,
    cost_estimate    DOUBLE,
    computed_at      DATETIME DEFAULT NOW(),
    UNIQUE KEY uq_machine_date (date, machine_id)
);

CREATE TABLE IF NOT EXISTS machine_alerts (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    date        DATE NOT NULL,
    machine_id  VARCHAR(100),
    alert_type  VARCHAR(100),
    severity    VARCHAR(20),
    message     TEXT,
    is_read     BOOLEAN DEFAULT FALSE,
    created_at  DATETIME DEFAULT NOW()
);

-- BLOC QUALITÉ
CREATE TABLE IF NOT EXISTS daily_quality_kpi (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    date                DATE NOT NULL,
    machine_id          VARCHAR(100),
    anomaly_rate        DOUBLE,
    first_pass_quality  DOUBLE,
    rejection_rate      DOUBLE,
    dpmo                DOUBLE,
    stability           DOUBLE,
    computed_at         DATETIME DEFAULT NOW(),
    UNIQUE KEY uq_quality_date_machine (date, machine_id)
);

CREATE TABLE IF NOT EXISTS quality_alerts (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    date        DATE NOT NULL,
    machine_id  VARCHAR(100),
    alert_type  VARCHAR(100),
    severity    VARCHAR(20),
    message     TEXT,
    is_read     BOOLEAN DEFAULT FALSE,
    created_at  DATETIME DEFAULT NOW()
);
```
