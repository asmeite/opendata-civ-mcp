import httpx

BASE_URL = "https://data.gouv.ci/data-fair/api/v1"


async def search_datasets_api(query: str, size: int = 10) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        params: dict[str, str | int] = {"size": size}
        if query:
            params["q"] = query
        response = await client.get(f"{BASE_URL}/catalog/datasets", params=params)
        response.raise_for_status()
        return response.json()


async def list_all_datasets_api() -> list[dict]:
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(f"{BASE_URL}/catalog/datasets", params={"size": 200})
        response.raise_for_status()
        return response.json().get("results", [])


async def get_dataset_info_api(slug: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{BASE_URL}/datasets/{slug}")
        response.raise_for_status()
        return response.json()


async def get_dataset_lines_api(slug: str, size: int = 100, filters: dict | None = None) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        params: dict[str, str | int] = {"size": size}
        if filters:
            # syntaxe data-fair : qs=COLONNE:"valeur" (format Elasticsearch)
            qs = " AND ".join(f'{k}:"{v}"' for k, v in filters.items())
            params["qs"] = qs
        response = await client.get(f"{BASE_URL}/datasets/{slug}/lines", params=params)
        response.raise_for_status()
        return response.json()
