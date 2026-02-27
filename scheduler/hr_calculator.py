from models.employee import Employee
from models.factory_log import FactoryLog
from models.daily_hr_kpi import DailyHrKpi
from models.hr_alert import HrAlert
from config import db
from datetime import date, datetime

# ============================================================
# SEUILS
# ============================================================
SEUIL_ABSENTEISME      = 0.15
SEUIL_ABSENTEISME_CRIT = 0.25
SEUIL_FATIGUE_WARN     = 3.0
SEUIL_FATIGUE_CRIT     = 5.0
SEUIL_PRODUCTIVITE     = 60.0
SEUIL_ROTATION         = 3


# ============================================================
# FONCTION PRINCIPALE — appelée par le scheduler
# ============================================================
def calculer_et_stocker_hr_kpi():
    today = date.today()
    shifts = ["Matin", "Après-midi", "Nuit", "ALL"]

    for shift in shifts:
        kpi = _calculer_kpi_shift(shift, today)
        if kpi:
            _upsert_daily_hr_kpi(kpi, shift, today)
            _generer_alertes(kpi, shift, today)

    db.session.commit()
    print(f"[HR Scheduler] ✅ KPI calculés pour {today} à {datetime.now().strftime('%H:%M:%S')}")


# ============================================================
# CALCUL KPI PAR SHIFT
# ============================================================
def _calculer_kpi_shift(shift, today):
    try:
        # Récupérer les employés selon shift
        query = Employee.query
        if shift != "ALL":
            query = query.filter_by(shift_travail=shift)
        employes = query.all()

        if not employes:
            return None

        total = len(employes)

        # --- Présence ---
        present_count = sum(1 for e in employes if e.statut_presence == "Présent")
        absent_count  = total - present_count
        absenteeism_rate = round(absent_count / total, 4)

        # --- Performance ---
        avg_productivity = round(
            sum(e.performance_moyenne for e in employes) / total, 2
        )
        avg_rendement = round(
            sum(e.taux_rendement for e in employes) / total, 2
        )

        # --- Fatigue ---
        fatigue_scores = []
        for e in employes:
            score = (
                e.retards_mois +
                e.heures_absence_mois / 8 +
                e.accidents_travail * 5 +
                e.maladies_professionnelles * 3
            ) / max(e.anciennete_annees, 1)
            fatigue_scores.append(score)

        fatigue_score = round(
            sum(fatigue_scores) / len(fatigue_scores), 3
        )

        # --- Risques ---
        rotation_risk_count    = sum(1 for e in employes if e.risque_depart == "Élevé")
        absenteisme_risk_count = sum(1 for e in employes if e.risque_absenteisme == "Élevé")

        # --- Séniorité ---
        avg_seniority = round(
            sum(e.anciennete_annees for e in employes) / total, 1
        )

        return {
            "present_count":          present_count,
            "absent_count":           absent_count,
            "absenteeism_rate":       absenteeism_rate,
            "avg_productivity":       avg_productivity,
            "avg_rendement":          avg_rendement,
            "fatigue_score":          fatigue_score,
            "rotation_risk_count":    rotation_risk_count,
            "absenteisme_risk_count": absenteisme_risk_count,
            "avg_seniority":          avg_seniority,
            "total":                  total,
            "employes":               employes
        }

    except Exception as e:
        print(f"[HR Calculator] ❌ Erreur calcul shift {shift} : {e}")
        return None


# ============================================================
# UPSERT daily_hr_kpi
# ============================================================
def _upsert_daily_hr_kpi(kpi, shift, today):
    """
    Met à jour ou insère les indicateurs RH pour un shift et une date donnés.
    Utilise no_autoflush pour éviter les IntegrityError lors des calculs rapides.
    """
    try:
        # On utilise no_autoflush pour empêcher SQLAlchemy de tenter une
        # insertion avant que la vérification ne soit terminée.
        with db.session.no_autoflush:
            # 1. On cherche si l'entrée existe déjà pour ce shift et ce jour
            existing = DailyHrKpi.query.filter_by(date=today, shift=shift).first()

            if existing:
                # 2. SI EXISTE : MISE À JOUR (UPDATE)
                existing.present_count = kpi["present_count"]
                existing.absent_count = kpi["absent_count"]
                existing.absenteeism_rate = kpi["absenteeism_rate"]
                existing.avg_productivity = kpi["avg_productivity"]
                existing.avg_rendement = kpi["avg_rendement"]
                existing.fatigue_score = kpi["fatigue_score"]
                existing.rotation_risk_count = kpi["rotation_risk_count"]
                existing.absenteisme_risk_count = kpi["absenteisme_risk_count"]
                existing.avg_seniority = kpi["avg_seniority"]
                existing.computed_at = datetime.now()
            else:
                # 3. SI NOUVEAU : CRÉATION (INSERT)
                nouvelle_ligne = DailyHrKpi(
                    date=today,
                    shift=shift,
                    present_count=kpi["present_count"],
                    absent_count=kpi["absent_count"],
                    absenteeism_rate=kpi["absenteeism_rate"],
                    avg_productivity=kpi["avg_productivity"],
                    avg_rendement=kpi["avg_rendement"],
                    fatigue_score=kpi["fatigue_score"],
                    rotation_risk_count=kpi["rotation_risk_count"],
                    absenteisme_risk_count=kpi["absenteisme_risk_count"],
                    avg_seniority=kpi["avg_seniority"]
                )
                db.session.add(nouvelle_ligne)

    except Exception as e:
        print(f"[HR Calculator] ❌ Erreur lors de l'UPSERT pour le shift {shift} : {e}")
        # En cas d'erreur, on annule les changements pour ne pas corrompre la session
        db.session.rollback()


# ============================================================
# GÉNÉRATION ALERTES
# ============================================================
def _generer_alertes(kpi, shift, today):
    alertes = []

    # Absentéisme
    if kpi["absenteeism_rate"] > SEUIL_ABSENTEISME:
        alertes.append(HrAlert(
            date       = today,
            shift      = shift,
            alert_type = "HIGH_ABSENTEEISM",
            severity   = "critical" if kpi["absenteeism_rate"] > SEUIL_ABSENTEISME_CRIT else "warning",
            message    = f"Taux absentéisme {shift} : {round(kpi['absenteeism_rate'] * 100, 1)}%"
        ))

    # Fatigue
    if kpi["fatigue_score"] > SEUIL_FATIGUE_CRIT:
        alertes.append(HrAlert(
            date       = today,
            shift      = shift,
            alert_type = "HIGH_FATIGUE",
            severity   = "critical",
            message    = f"Score fatigue critique shift {shift} : {kpi['fatigue_score']}"
        ))
    elif kpi["fatigue_score"] > SEUIL_FATIGUE_WARN:
        alertes.append(HrAlert(
            date       = today,
            shift      = shift,
            alert_type = "HIGH_FATIGUE",
            severity   = "warning",
            message    = f"Score fatigue élevé shift {shift} : {kpi['fatigue_score']}"
        ))

    # Rotation
    if kpi["rotation_risk_count"] >= SEUIL_ROTATION:
        alertes.append(HrAlert(
            date       = today,
            shift      = shift,
            alert_type = "HIGH_ROTATION_RISK",
            severity   = "warning",
            message    = f"{kpi['rotation_risk_count']} employés risque départ élevé — shift {shift}"
        ))

    # Productivité basse
    if kpi["avg_productivity"] < SEUIL_PRODUCTIVITE:
        alertes.append(HrAlert(
            date       = today,
            shift      = shift,
            alert_type = "LOW_PRODUCTIVITY",
            severity   = "warning",
            message    = f"Productivité moyenne basse shift {shift} : {kpi['avg_productivity']}"
        ))

    # Alertes individuelles — accidents (shift ALL uniquement pour éviter doublons)
    if shift == "ALL":
        for e in kpi["employes"]:
            if e.accidents_travail > 0:
                alertes.append(HrAlert(
                    date        = today,
                    employee_id = e.employee_id,
                    shift       = e.shift_travail,
                    alert_type  = "ACCIDENT_REPORTED",
                    severity    = "critical",
                    message     = f"{e.prenom} {e.nom} — {e.accidents_travail} accident(s) signalé(s)"
                ))

    # Insert sans doublons
    for alerte in alertes:
        existe = HrAlert.query.filter_by(
            date        = today,
            shift       = alerte.shift,
            alert_type  = alerte.alert_type,
            employee_id = alerte.employee_id
        ).first()
        if not existe:
            db.session.add(alerte)