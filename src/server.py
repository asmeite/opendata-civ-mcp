from mcp.server.fastmcp import FastMCP
from src.tools import search_datasets, get_dataset_lines, get_dataset_info, list_topics, get_dataset_file

mcp = FastMCP("opendata-civ-mcp")


@mcp.tool()
async def search_datasets_tool(query: str, size: int = 10) -> list[dict]:
    """
    Recherche des jeux de données dans le portail open data du gouvernement ivoirien (data.gouv.ci).

    Args:
        query: Mots-clés de recherche en français (ex: "électricité", "déforestation", "éducation")
        size: Nombre de résultats à retourner (défaut 10, max 50)

    Returns:
        Liste de datasets avec slug, titre, description, colonnes disponibles et thématiques
    """
    return await search_datasets(query=query, size=size)


@mcp.tool()
async def list_topics_tool() -> dict:
    """
    Liste toutes les thématiques disponibles sur le portail data.gouv.ci
    avec le nombre de datasets par thématique.
    À appeler en premier pour découvrir ce qui existe avant de chercher un dataset.

    Returns:
        Dictionnaire {"Thématique": nb_datasets} trié par ordre décroissant
    """
    return await list_topics()


@mcp.tool()
async def get_dataset_info_tool(slug: str) -> dict:
    """
    Récupère les métadonnées complètes d'un jeu de données du portail data.gouv.ci.
    Utile pour connaître les colonnes disponibles et leurs valeurs possibles avant de filtrer.

    Args:
        slug: Identifiant du dataset (obtenu via search_datasets_tool)

    Returns:
        titre, description, nb lignes, source, topics, schéma des colonnes avec valeurs possibles
    """
    return await get_dataset_info(slug=slug)


@mcp.tool()
async def get_dataset_lines_tool(slug: str, limit: int = 100, filters: dict | None = None) -> dict:
    """
    Récupère les données réelles d'un jeu de données du portail data.gouv.ci.

    Args:
        slug: Identifiant du dataset (obtenu via search_datasets_tool)
        limit: Nombre de lignes à retourner (défaut 100, max 1000)
        filters: Filtres optionnels {"colonne": "valeur"} (ex: {"DREN": "Abidjan 1"})

    Returns:
        {"total": int, "results": list[dict]}
    """
    return await get_dataset_lines(slug=slug, limit=limit, filters=filters)


@mcp.tool()
async def get_dataset_file_tool(slug: str, format: str = "csv") -> dict:
    """
    Retourne l'URL de téléchargement direct d'un dataset du portail data.gouv.ci.

    Args:
        slug: Identifiant du dataset (obtenu via search_datasets_tool)
        format: Format souhaité — "csv" ou "xlsx" (défaut: "csv")

    Returns:
        URL de téléchargement, nom du fichier et taille en octets
    """
    return await get_dataset_file(slug=slug, format=format)


if __name__ == "__main__":
    mcp.run()
