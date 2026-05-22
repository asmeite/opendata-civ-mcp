from collections import Counter
from src.client.datagouv_client import list_all_datasets_api


async def list_topics() -> dict:
    """
    Liste toutes les thématiques disponibles sur data.gouv.ci
    avec le nombre de datasets par thématique.

    Returns:
        Dictionnaire {"Thématique": nb_datasets} trié par ordre décroissant
    """
    datasets = await list_all_datasets_api()
    counter = Counter()
    for ds in datasets:
        for topic in ds.get("topics", []):
            counter[topic["title"]] += 1
    return dict(counter.most_common())
