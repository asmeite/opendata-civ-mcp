from src.client.datagouv_client import get_dataset_info_api


async def get_dataset_info(slug: str) -> dict:
    """
    Récupère les métadonnées complètes d'un jeu de données.

    Args:
        slug: Identifiant du dataset (obtenu via search_datasets)

    Returns:
        slug, titre, description, nb lignes, source, topics,
        schéma des colonnes avec valeurs possibles (enum)
    """
    data = await get_dataset_info_api(slug=slug)
    return {
        "slug": data.get("slug"),
        "title": data.get("title"),
        "description": data.get("description", "").strip(),
        "count": data.get("count"),
        "origin": data.get("origin"),
        "url_portail": data.get("page"),
        "updated_at": data.get("dataUpdatedAt"),
        "topics": [t.get("title") for t in data.get("topics", [])],
        "license": data.get("license", {}).get("title"),
        "schema": [
            {
                "key": col["key"],
                "type": col["type"],
                "enum": col.get("enum", []),
            }
            for col in data.get("schema", [])
            if not col.get("x-calculated")
        ],
    }
