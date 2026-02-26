import httpx
from server import mcp

@mcp.tool()
async def get_rendement_usine() -> dict:
    """
    Appelle l'API Flask pour récupérer le rendement global de l'usine :
    OEE global, taux de gaspillage, taux de complétion, meilleur/pire atelier,
    rendement par atelier et indice de résilience.
    """
    url = "http://localhost:5000/rendement/usine"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        return {"error": "Impossible de récupérer le rendement de l'usine"}

    return response.json()
