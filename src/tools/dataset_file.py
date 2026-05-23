from src.client.datagouv_client import get_dataset_info_api

BASE_URL = "https://data.gouv.ci/data-fair/api/v1"

FORMATS = {
    "csv": "full",
    "xlsx": "raw",
}


async def get_dataset_file(slug: str, format: str = "csv") -> dict:
    """
    Retourne l'URL de téléchargement direct d'un dataset.

    Args:
        slug: Identifiant du dataset (obtenu via search_datasets)
        format: Format souhaité — "csv" ou "xlsx" (défaut: "csv")

    Returns:
        {"slug": str, "format": str, "url": str, "size": int, "filename": str}
    """
    format = format.lower()
    if format not in FORMATS:
        raise ValueError(f"Format non supporté : '{format}'. Choisir 'csv' ou 'xlsx'.")

    key = FORMATS[format]
    data = await get_dataset_info_api(slug=slug)

    # récupère le nom et la taille du fichier depuis storage.dataFiles
    file_key = "original" if format == "xlsx" else "normalized"
    data_files = data.get("storage", {}).get("dataFiles", [])
    fichier = next((f for f in data_files if f.get("key") == file_key), None)

    return {
        "slug": slug,
        "format": format,
        "filename": fichier.get("name") if fichier else None,
        "size_bytes": fichier.get("size") if fichier else None,
        "url": f"{BASE_URL}/datasets/{slug}/{key}",
        "url_portail": data.get("page") or f"https://data.gouv.ci/datasets/{slug}",
    }
