import httpx
from server import mcp

@mcp.tool()
async def get_rendement_machine(machine_id: str) -> dict:
    """
    Appelle l'API Flask pour récupérer le rendement d'une machine (OEE, disponibilité,
    taux d'utilisation, classement atelier, top 5 employés, indices cachés).
    """
    url = f"http://localhost:5000/rendement/machine/{machine_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        return {"error": f"Impossible de récupérer la machine {machine_id}"}

    return response.json()
