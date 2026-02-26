import httpx
from server import mcp

@mcp.tool()
async def get_rendement_taches() -> dict:
    """
    Appelle l'API Flask pour récupérer les statistiques globales sur les tâches :
    taux de complétion, anomalies, efficacité temps réel, rendement par produit et par shift.
    """
    url = "http://localhost:5000/rendement/taches"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        return {"error": "Impossible de récupérer le rendement des tâches"}

    return response.json()
