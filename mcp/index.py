from server import mcp
import tools.employeeTools   # employe : get_rendement_employe, get_historique_employe
import tools.machineTools    # machine : get_rendement_machine
import tools.atelierTools    # atelier : get_rendement_atelier, get_top10_atelier, get_flop10_atelier
import tools.tachesTools     # taches  : get_rendement_taches
import tools.usineTools        # usine        : get_rendement_usine
import tools.globalTools       # global       : get_rendement_global
import tools.dispatchingTools  # dispatching  : get_dispatching

def main():
    print("MCP server started, waiting for requests...")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()