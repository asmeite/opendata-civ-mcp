"""
Test du tool get_dataset_file (URLs corrigées)
"""

import asyncio
from src.tools.dataset_file import get_dataset_file

SLUG = "synthese-du-primaire-public-et-prive-par-dren-et-par-classe-2007-2008"


async def main():
    for fmt in ["csv", "xlsx"]:
        print(f">>> format='{fmt}'")
        result = await get_dataset_file(slug=SLUG, format=fmt)
        print(f"  Fichier : {result['filename']}")
        print(f"  Taille  : {result['size_bytes']} octets")
        print(f"  URL     : {result['url']}")
        print()


asyncio.run(main())
