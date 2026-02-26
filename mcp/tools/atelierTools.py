import httpx
from server import mcp

@mcp.tool()
async def get_rendement_atelier(nom: str) -> dict:
    """
    Appelle l'API Flask pour récupérer le rendement d'un atelier :
    OEE moyen, score employés, benchmark vs autres ateliers, équilibre de charge.
    """
    url = f"http://localhost:5000/rendement/atelier/{nom}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        return {"error": f"Impossible de récupérer l'atelier {nom}"}

    return response.json()


@mcp.tool()
async def get_top10_atelier(nom: str) -> dict:
    """
    Retourne le top 10 des employés les plus performants d'un atelier.
    """
    url = f"http://localhost:5000/rendement/atelier/{nom}/top10"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        return {"error": f"Impossible de récupérer le top 10 de l'atelier {nom}"}

    return response.json()


@mcp.tool()
async def get_flop10_atelier(nom: str) -> dict:
    """
    Retourne le flop 10 des employés les moins performants d'un atelier.
    """
    url = f"http://localhost:5000/rendement/atelier/{nom}/flop10"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        return {"error": f"Impossible de récupérer le flop 10 de l'atelier {nom}"}

    return response.json()
