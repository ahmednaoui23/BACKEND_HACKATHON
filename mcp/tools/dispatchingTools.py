import httpx
from server import mcp

@mcp.tool()
async def get_dispatching() -> dict:
    """
    Appelle l'API Flask pour lancer l'algorithme génétique de dispatching des employés.
    Retourne les diagnostics (nombre de tâches, employés), le résumé des solutions GA,
    la meilleure solution globale et le plan d'affectation détaillé par employé
    (tâches assignées, temps total).
    """
    url = "http://localhost:5000/dispatching"

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.get(url)

    if response.status_code != 200:
        return {"error": "Impossible de récupérer le plan de dispatching"}

    return response.json()

@mcp.tool()
async def get_dispatching_hungarian() -> dict:
    """
    Appelle l'API Flask pour lancer l'algorithme de dispatching basé sur l'algorithme Hongrois.
    Retourne le plan d'affectation optimal (employé par tâche machine/produit)
    en minimisant le temps total d'exécution.
    """
    url = "http://localhost:5000/dispatching/hungarian"

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.get(url)

    if response.status_code != 200:
        return {"error": "Impossible de récupérer le plan de dispatching hongrois"}

    return response.json()

@mcp.tool()
async def get_worst_real_dispatching(day: str) -> dict:
    """
    Appelle l'API Flask pour récupérer le pire dispatching réel pour un jour donné.
    Pour chaque combinaison machine/produit, retourne l'employé ayant eu le temps
    d'exécution le plus élevé ce jour-là.

    Paramètre :
        day : date au format YYYY-MM-DD (ex: "2024-01-15")
    """
    url = f"http://localhost:5000/worst_real_dispatching?day={day}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)

    if response.status_code != 200:
        return {"error": f"Impossible de récupérer le pire dispatching pour le jour {day}"}

    return response.json()
