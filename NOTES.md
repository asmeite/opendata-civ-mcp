# Notes API data.gouv.ci

## Endpoints

| Action | Endpoint |
|---|---|
| Lister / rechercher des datasets | `GET /catalog/datasets?q=...&size=N` |
| Détail d'un dataset | `GET /datasets/{slug}` |
| Lignes de données | `GET /datasets/{slug}/lines?size=N` |

> Utiliser le `slug` dans les URLs, **pas** l'`id` court — l'`id` retourne 404.

---

## Structure de la réponse catalogue

```
{
  "count": 177,       ← total de datasets sur le portail
  "results": [...]    ← datasets retournés
}
```

Champs utiles par dataset :

| Champ | Utilité MCP |
|---|---|
| `slug` | clé pour construire toutes les URLs API |
| `title` | nom lisible du dataset |
| `description` | contexte pour l'IA |
| `count` | nombre de lignes disponibles |
| `origin` | source ministérielle |
| `topics` | thématique (Education, Energie…) |
| `schema` | colonnes dispo (exclure celles avec `x-calculated: true`) |
| `href` | URL API complète du dataset |

---

## URLs de téléchargement

- CSV : `GET /datasets/{slug}/full`
- XLSX : `GET /datasets/{slug}/raw`
- Les endpoints `/data-files/{key}` retournent 404 — ne pas utiliser.

## Points de vigilance

- **Slugs avec caractères spéciaux** : certains slugs contiennent des apostrophes (`l'ecole`) et des parenthèses (`(2012-2013)`) — à encoder correctement dans les URLs (`httpx` le fait automatiquement).
- **Noms de colonnes non normalisés** : les `key` du schéma reflètent les noms bruts du fichier source (`Cl__Péd_`, `DREN-ET`) — ne pas supposer un format propre.
- **Colonnes internes à exclure** : `_id`, `_i`, `_rand` ont `x-calculated: true` — inutiles pour l'IA.
- **Recherche full-text** : le paramètre `q` est géré côté serveur data.gouv.ci, pas par nous.

---

## Filtres sur les lignes

Syntaxe data-fair : paramètre `qs` avec format Elasticsearch.
```
GET /datasets/{slug}/lines?qs=DREN:"Abidjan 1"
```
Plusieurs filtres : `qs=DREN:"Abidjan 1" AND CLASSE:"CP1"`

Les syntaxes `eq:COLONNE` et `COLONNE=valeur` ne fonctionnent pas.

## Avancement des tools

- [x] `search_datasets(query, size)` — fonctionnel et testé
- [x] `get_dataset_lines(slug, filters, limit)` — fonctionnel et testé
- [x] `get_dataset_info(slug)` — fonctionnel et testé
- [x] `list_topics()` — fonctionnel et testé (agrégation côté serveur, 1 appel API)
- [x] `get_dataset_file(slug, format)` — fonctionnel et testé
- [ ] `list_topics()`
