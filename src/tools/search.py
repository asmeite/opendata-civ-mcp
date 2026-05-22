from src.client.datagouv_client import search_datasets_api


def _format_dataset(ds: dict) -> dict:
    return {
        "slug": ds.get("slug"),
        "title": ds.get("title"),
        "description": ds.get("description", "")[:300],
        "count": ds.get("count"),
        "origin": ds.get("origin"),
        "topics": [t.get("title") for t in ds.get("topics", [])],
        "schema": [
            {"key": col["key"], "type": col["type"]}
            for col in ds.get("schema", [])
            if not col.get("x-calculated")
        ],
    }


async def search_datasets(query: str, size: int = 10) -> list[dict]:
    """
    Recherche des jeux de données dans le portail open data data.gouv.ci.

    Args:
        query: Mots-clés de recherche en français
        size: Nombre de résultats à retourner (défaut 10, max 50)

    Returns:
        Liste de datasets avec slug, titre, description, colonnes, topics
    """
    data = await search_datasets_api(query=query, size=size)
    results = data.get("results", [])
    return [_format_dataset(ds) for ds in results]
