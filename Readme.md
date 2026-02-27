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
│   ├── daily_hr_kpi.py
│   ├── hr_alert.py
│   ├── daily_machine_kpi.py
│   ├── machine_alert.py
│   ├── daily_quality_kpi.py
│   ├── quality_alert.py
│   ├── daily_production_kpi.py
│   └── production_alert.py
├── routes/
│   ├── __init__.py
│   ├── employe_routes.py
│   ├── machine_routes.py
│   ├── atelier_routes.py
│   ├── taches_routes.py
│   ├── usine_routes.py
│   ├── global_routes.py
│   ├── quality_routes.py
│   └── production_routes.py
├── services/
│   ├── __init__.py
│   ├── employe_service.py
│   ├── machine_service.py
│   ├── atelier_service.py
│   ├── taches_service.py
│   ├── usine_service.py
│   ├── global_service.py
│   ├── quality_service.py
│   └── production_service.py
└── scheduler/
    ├── __init__.py
    ├── hr_calculator.py
    ├── hr_scheduler.py
    ├── machine_calculator.py
    ├── machine_scheduler.py
    ├── quality_calculator.py
    ├── quality_scheduler.py
    ├── production_calculator.py
    └── production_scheduler.py
```

---

## 🗄️ Base de données

### Tables existantes

| Table | Description |
|---|---|
| `employee` | Données RH, performance, présence, rendement, risques |
| `machines_realiste_textile` | Données machines, pannes, OEE, énergie, rendement |
| `factory_logs` | Logs de tâches en temps réel par machine et employé |

### Tables KPI dédiées

| Table | Description | Fréquence calcul |
|---|---|---|
| `daily_production_kpi` | KPI production par shift et atelier | Toutes les 15 min |
| `production_alerts` | Alertes production (rendement, OEE, interruptions) | Toutes les 15 min |
| `daily_hr_kpi` | KPI RH agrégés par shift et par jour | Toutes les 15 min |
| `hr_alerts` | Alertes RH (fatigue, absentéisme, rotation) | Toutes les 15 min |
| `daily_machine_kpi` | KPI machines par jour (MTBF, MTTR, disponibilité) | Toutes les 15 min |
| `machine_alerts` | Alertes machines (pannes, anomalies, sous-utilisation) | Toutes les 15 min |
| `daily_quality_kpi` | KPI qualité par machine et global usine | Toutes les 15 min |
| `quality_alerts` | Alertes qualité (anomalies, rejets, DPMO) | Toutes les 15 min |

---

## 🗄️ Créer les tables KPI (SQL)

Exécutez ce script dans MySQL Workbench pour créer les 8 tables KPI dédiées :

```sql
-- BLOC PRODUCTION
CREATE TABLE IF NOT EXISTS daily_production_kpi (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    date              DATE NOT NULL,
    shift             VARCHAR(50) NOT NULL,
    atelier           VARCHAR(100) NOT NULL DEFAULT 'ALL',
    taux_completion   DOUBLE,
    efficiency        DOUBLE,
    stability         DOUBLE,
    global_yield      DOUBLE,
    oee               DOUBLE,
    duration_ratio    DOUBLE,
    cadence           DOUBLE,
    interruption_rate DOUBLE,
    computed_at       DATETIME DEFAULT NOW(),
    UNIQUE KEY uq_prod_date_shift_atelier (date, shift, atelier)
);

CREATE TABLE IF NOT EXISTS production_alerts (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    date        DATE NOT NULL,
    shift       VARCHAR(50),
    atelier     VARCHAR(100),
    alert_type  VARCHAR(100),
    severity    VARCHAR(20),
    message     TEXT,
    is_read     BOOLEAN DEFAULT FALSE,
    created_at  DATETIME DEFAULT NOW()
);

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

### 5 — Créer les tables KPI
Exécutez le script SQL ci-dessus dans MySQL Workbench.

### 6 — Lancer l'API
```bash
python app.py
```

Le scheduler démarre immédiatement et calcule les KPI toutes les 15 minutes sur **toutes les données disponibles**.

L'API tourne sur **http://127.0.0.1:5000**

---

## 🔌 Endpoints API — 62 endpoints

### 📌 Bloc 1 — Production

| Méthode | URL | Description |
|---|---|---|
| GET | `/production/kpis/today` | KPI global usine tous shifts |
| GET | `/production/kpis/shift/<shift>` | KPI par shift tous ateliers |
| GET | `/production/kpis/atelier/<atelier>` | KPI par atelier tous shifts |
| GET | `/production/kpis/aggregated` | KPI agrégés depuis daily_production_kpi |
| GET | `/production/kpis/series?shift=ALL&atelier=ALL` | Courbes mois précédent vs actuel |
| GET | `/production/alerts` | Alertes production actives |
| GET | `/production/alerts?severity=critical` | Alertes critiques uniquement |
| PATCH | `/production/alerts/<id>/read` | Marquer une alerte comme lue |

### 🔧 Bloc 2 — Machines

| Méthode | URL | Description |
|---|---|---|
| GET | `/machines` | Liste toutes les machines |
| GET | `/machines?atelier=Coupe` | Filtrer par atelier |
| GET | `/machines?etat=en panne` | Filtrer par état |
| GET | `/machines/<id>` | Détail complet machine |
| POST | `/machines` | Créer une machine |
| PUT | `/machines/<id>` | Modifier une machine |
| DELETE | `/machines/<id>` | Supprimer une machine |
| GET | `/rendement/machine/<id>` | Fiche rendement machine |
| GET | `/machine/kpis/today` | KPI de toutes les machines |
| GET | `/machine/kpis/<machine_id>` | KPI d'une machine précise |
| GET | `/machine/kpis/atelier/<atelier>` | KPI machines d'un atelier |
| GET | `/machine/kpis/aggregated` | KPI agrégés depuis daily_machine_kpi |
| GET | `/machine/kpis/series/<machine_id>` | Courbes mois précédent vs actuel |
| GET | `/machine/alerts` | Alertes machines actives |
| GET | `/machine/alerts?severity=critical` | Alertes critiques uniquement |
| PATCH | `/machine/alerts/<id>/read` | Marquer une alerte comme lue |

### 👷 Bloc 3 — Ressources Humaines

| Méthode | URL | Description |
|---|---|---|
| GET | `/employes` | Liste tous les employés |
| GET | `/employes?departement=Coupe` | Filtrer par département |
| GET | `/employes?shift=Matin` | Filtrer par shift |
| GET | `/employes?poste=Opérateur` | Filtrer par poste |
| GET | `/employes/<id>` | Profil complet employé |
| POST | `/employes` | Créer un employé |
| PUT | `/employes/<id>` | Modifier un employé |
| DELETE | `/employes/<id>` | Supprimer un employé |
| GET | `/rendement/employe/<id>` | Fiche rendement employé |
| GET | `/rendement/employe/<id>/historique` | Historique et évolution |
| GET | `/hr/kpis/employes/today` | KPI de tous les employés |
| GET | `/hr/kpis/employe/<id>` | KPI d'un employé précis |
| GET | `/hr/kpis/shift/<shift>` | KPI employés d'un shift |
| GET | `/hr/kpis/departement/<departement>` | KPI employés d'un atelier |
| GET | `/hr/kpis/today` | KPI agrégés par shift |
| GET | `/hr/kpis/series?shift=ALL` | Courbes mois précédent vs actuel |
| GET | `/hr/alerts` | Alertes RH actives |
| GET | `/hr/alerts?severity=critical` | Alertes critiques uniquement |
| PATCH | `/hr/alerts/<id>/read` | Marquer une alerte comme lue |

### 📊 Bloc 4 — Qualité

| Méthode | URL | Description |
|---|---|---|
| GET | `/quality/kpis/today` | KPI qualité toutes machines |
| GET | `/quality/kpis/machine/<machine_id>` | KPI qualité machine précise |
| GET | `/quality/kpis/atelier/<atelier>` | KPI qualité d'un atelier |
| GET | `/quality/kpis/global` | KPI qualité global usine |
| GET | `/quality/kpis/series?machine_id=ALL` | Courbes mois précédent vs actuel |
| GET | `/quality/alerts` | Alertes qualité actives |
| GET | `/quality/alerts?severity=critical` | Alertes critiques uniquement |
| PATCH | `/quality/alerts/<id>/read` | Marquer une alerte comme lue |

### 🏢 Ateliers

| Méthode | URL | Description |
|---|---|---|
| GET | `/ateliers` | Liste tous les ateliers |
| GET | `/ateliers/<nom>/employes` | Employés d'un atelier |
| GET | `/ateliers/<nom>/machines` | Machines d'un atelier |
| GET | `/ateliers/<nom>/adn` | ADN complet atelier |
| GET | `/rendement/atelier/<nom>` | Rendement global atelier |
| GET | `/rendement/atelier/<nom>/top10` | Top 10 performers |
| GET | `/rendement/atelier/<nom>/flop10` | Flop 10 à surveiller |
| GET | `/ateliers/comparer?a=X&b=Y` | Comparer 2 ateliers |

### 🏭 Usine

| Méthode | URL | Description |
|---|---|---|
| GET | `/usine/pouls` | Snapshot temps réel usine |
| GET | `/usine/risques` | Carte des risques |
| GET | `/usine/rapport` | Rapport mensuel complet |
| GET | `/rendement/usine` | Rendement global usine |
| GET | `/rendement/global` | Tout en une seule réponse |
| GET | `/rendement/taches` | Stats globales tâches |

---

## 🤖 Schedulers — Calcul KPI automatique

```
Au démarrage + toutes les 15 minutes
    ↓
├── production_calculator → daily_production_kpi + production_alerts
├── hr_calculator         → daily_hr_kpi + hr_alerts
├── machine_calculator    → daily_machine_kpi + machine_alerts
└── quality_calculator    → daily_quality_kpi + quality_alerts

Chaque nuit
├── 00h30 → consolidation production
├── 01h00 → consolidation RH
├── 01h30 → consolidation machines
└── 02h00 → consolidation qualité
```

Le scheduler calcule sur **toutes les données disponibles** — pas uniquement les données du jour.

---

## 📊 KPI calculés par bloc

### Bloc 1 — Production
- **Global Yield** `(taux_completion×0.40 + efficiency×0.35 + stability×0.25)`
- **OEE** `disponibilité × performance × qualité`
- **Taux Completion** tâches completées / total
- **Efficiency** durée théorique / durée réelle
- **Stability** `1 - coefficient de variation des durées`
- **Duration Ratio** durée réelle / durée théorique
- **Cadence** nb tâches / heure
- **Interruption Rate** tâches interrompues / total

### Bloc 2 — Machines
- **MTBF** `160h / pannes_mois`
- **MTTR** `MTBF × 10%`
- **Disponibilité** état machine opérationnelle
- **Taux d'utilisation** tâches actives / capacité
- **Taux anomalies** anomalies / total tâches
- **Coût estimé pannes** `pannes_mois × 150€`

### Bloc 3 — RH
- **Score Rendement** `(taux_rendement×0.40 + performance×0.35 + evaluation×0.15 + ponctualité×0.10)`
- **Score Fatigue** `(retards + absences/8 + accidents×5 + maladies×3) / ancienneté`
- **Taux présence**, **Taux ponctualité**
- **Taux completion tâches**, **Taux anomalies**
- **Risque absentéisme**, **Risque départ**
- **Indice burnout**, **Rendement nocturne ajusté**

### Bloc 4 — Qualité
- **Anomaly Rate** anomalies / total tâches
- **First Pass Quality** `1 - anomaly_rate`
- **Rejection Rate** tâches Failed / total
- **DPMO** `(anomalies / (total × 5)) × 1,000,000`
- **Stabilité processus** rendement_machine moyen

---

## 🚨 Types d'alertes automatiques

### Production
| Alert Type | Déclencheur |
|---|---|
| `LOW_GLOBAL_YIELD` | Rendement < 70% (critical < 55%) |
| `LOW_OEE` | OEE < 65% (critical < 50%) |
| `HIGH_INTERRUPTION` | Interruptions > 15% (critical > 30%) |
| `LOW_COMPLETION` | Complétion < 70% |

### RH
| Alert Type | Déclencheur |
|---|---|
| `HIGH_ABSENTEEISM` | Absentéisme > 15% (critical > 25%) |
| `HIGH_FATIGUE` | Fatigue > 3.0 (critical > 5.0) |
| `HIGH_ROTATION_RISK` | Nb risque départ ≥ 3 |
| `LOW_PRODUCTIVITY` | Productivité < 60 |
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

```
# Production
GET http://127.0.0.1:5000/production/kpis/today
GET http://127.0.0.1:5000/production/kpis/aggregated
GET http://127.0.0.1:5000/production/kpis/shift/Matin
GET http://127.0.0.1:5000/production/kpis/atelier/Coupe
GET http://127.0.0.1:5000/production/alerts

# RH
GET http://127.0.0.1:5000/hr/kpis/today
GET http://127.0.0.1:5000/hr/kpis/employes/today
GET http://127.0.0.1:5000/hr/kpis/shift/Matin
GET http://127.0.0.1:5000/hr/kpis/departement/Couture
GET http://127.0.0.1:5000/hr/alerts

# Machines
GET http://127.0.0.1:5000/machine/kpis/today
GET http://127.0.0.1:5000/machine/kpis/aggregated
GET http://127.0.0.1:5000/machine/alerts

# Qualité
GET http://127.0.0.1:5000/quality/kpis/global
GET http://127.0.0.1:5000/quality/kpis/today
GET http://127.0.0.1:5000/quality/alerts

# Usine
GET http://127.0.0.1:5000/usine/pouls
GET http://127.0.0.1:5000/rendement/usine
```

---

## 🔄 Flux temps réel

```
Données dans factory_logs + employee + machines
        ↓
Scheduler déclenché toutes les 15 min
        ↓
Calcul KPI sur TOUTES les données disponibles
        ↓
UPSERT dans les 4 tables KPI dédiées
INSERT alertes automatiques (sans doublons)
        ↓
React poll GET endpoints toutes les 30s
        ↓
Courbes mises à jour en live
```

---

## 📦 Requirements

```
Flask
Flask-CORS
Flask-SQLAlchemy
SQLAlchemy
PyMySQL
APScheduler
modelcontextprotocol
httpx
asyncio
mcp
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

- Remplacer `<id>` par un vrai `employee_id` ex: `E001`
- Remplacer `<nom>` par un vrai nom d'atelier ex: `Coupe`
- Les shifts valides sont : `Matin`, `Après-midi`, `Nuit`, `ALL`
- Le scheduler calcule sur toutes les données — pas uniquement aujourd'hui
- Les alertes avec `is_read=true` n'apparaissent plus dans les endpoints alerts
- Le DPMO est calculé avec 5 opportunités par unité (modifiable dans `quality_calculator.py`)
- Le coût panne unitaire est 150€ (modifiable dans `machine_calculator.py`)