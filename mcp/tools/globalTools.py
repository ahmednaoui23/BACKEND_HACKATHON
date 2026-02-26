import httpx
from server import mcp

@mcp.tool()
async def get_rendement_global() -> dict:
    """
    Appelle l'API Flask pour récupérer une vue consolidée de toute l'usine :
    résumé usine, tâches, ateliers, top/flop employés et machines.
    """
    url = "http://localhost:5000/rendement/global"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        return {"error": "Impossible de récupérer le rendement global"}

    return response.json()
