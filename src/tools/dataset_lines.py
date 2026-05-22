from src.client.datagouv_client import get_dataset_lines_api

INTERNAL_FIELDS = {"_id", "_i", "_rand", "_score"}


def _nettoyer_ligne(ligne: dict) -> dict:
    return {k: v for k, v in ligne.items() if k not in INTERNAL_FIELDS}


async def get_dataset_lines(slug: str, limit: int = 100, filters: dict | None = None) -> dict:
    """
    Récupère les données réelles d'un jeu de données.

    Args:
        slug: Identifiant du dataset (obtenu via search_datasets)
        limit: Nombre de lignes à retourner (défaut 100, max 1000)
        filters: Filtres optionnels {"colonne": "valeur"}

    Returns:
        {"total": int, "results": list[dict]}
    """
    data = await get_dataset_lines_api(slug=slug, size=limit, filters=filters)
    return {
        "total": data.get("total"),
        "results": [_nettoyer_ligne(row) for row in data.get("results", [])],
    }