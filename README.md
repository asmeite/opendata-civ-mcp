---
title: Données Publiques Côte d'Ivoire
emoji: 🟠
colorFrom: yellow
colorTo: green
sdk: streamlit
sdk_version: "1.45.0"
app_file: demo/app.py
pinned: false
---

# opendata-civ-mcp

Serveur MCP connecté au portail open data officiel de Côte d'Ivoire — [data.gouv.ci](https://data.gouv.ci).

Permet à tout agent IA de rechercher, analyser et télécharger les données publiques ivoiriennes en langage naturel.

## Fonctionnalités

- Exploration de 177 jeux de données publics
- Recherche par mots-clés et thématiques
- Lecture des données réelles avec filtres
- Téléchargement direct en CSV ou XLSX
- Interface conversationnelle en français

## Outils MCP disponibles

| Outil | Description |
|---|---|
| `list_topics` | Lister les thématiques disponibles |
| `search_datasets` | Rechercher des datasets par mots-clés |
| `get_dataset_info` | Obtenir le schéma et les métadonnées |
| `get_dataset_lines` | Lire les données réelles |
| `get_dataset_file` | Obtenir le lien de téléchargement |

## Installation locale

```bash
git clone https://github.com/aboubakarSM/opendata-civ-mcp
cd opendata-civ-mcp
pip install -r requirements.txt
```

Créer un fichier `.env` :

```
CEREBRAS_API_KEY=votre_clé
```

Lancer l'interface :

```bash
streamlit run demo/app.py
```

## Données

Toutes les données proviennent du portail officiel [data.gouv.ci](https://data.gouv.ci) sous **Licence Ouverte 2.0**.

## Auteur

**Aboubakar Sidik MEITE** — Ingénieur Data & IA  
[smeite20@gmail.com](mailto:smeite20@gmail.com)
