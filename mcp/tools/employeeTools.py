import httpx
from server import mcp

@mcp.tool()
async def get_rendement_employe(employee_id: str) -> dict:
    """
    Appelle l'API Flask pour récupérer le rendement complet d'un employé :
    présence, ponctualité, score global, classement atelier, meilleur shift,
    indice burnout et rendement nocturne ajusté.
    """
    url = f"http://localhost:5000/rendement/employe/{employee_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        return {"error": f"Impossible de récupérer l'employé {employee_id}"}

    return response.json()


@mcp.tool()
async def get_historique_employe(employee_id: str) -> dict:
    """
    Appelle l'API Flask pour récupérer l'historique d'un employé.
    """
    url = f"http://localhost:5000/rendement/employe/{employee_id}/historique"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        return {"error": f"Impossible de récupérer l'historique de l'employé {employee_id}"}

    return response.json()