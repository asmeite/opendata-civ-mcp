# Cahier des Charges — opendata-civ-mcp MCP Server
## Connecter l'Intelligence Artificielle aux Données Publiques de Côte d'Ivoire

---

**Porteur de projet :** Aboubakar Sidik MEITE — Ingénieur Data  
**Contact :** smeite20@gmail.com — +33 06 56 67 50 62  
**Destinataire :** Ministère de la Transition Numérique et de la Digitalisation — République de Côte d'Ivoire  
**Version :** 1.0  
**Date :** Mai 2026  
**Statut :** Soumis pour financement

---

## Table des matières

1. [Contexte et enjeux](#1-contexte-et-enjeux)
2. [Présentation du projet](#2-présentation-du-projet)
3. [Objectifs](#3-objectifs)
4. [Périmètre fonctionnel](#4-périmètre-fonctionnel)
5. [Architecture technique](#5-architecture-technique)
6. [Spécifications techniques détaillées](#6-spécifications-techniques-détaillées)
7. [Plan de développement](#7-plan-de-développement)
8. [Livrables](#8-livrables)
9. [Critères de succès](#9-critères-de-succès)
10. [Alignement stratégique SNNCI](#10-alignement-stratégique-snnci)
11. [Budget prévisionnel](#11-budget-prévisionnel)
12. [Profil du porteur de projet](#12-profil-du-porteur-de-projet)
13. [Risques et mesures d'atténuation](#13-risques-et-mesures-datténuation)
14. [Glossaire](#14-glossaire)

---

## 1. Contexte et enjeux

### 1.1 La transition numérique ivoirienne

La Côte d'Ivoire s'est engagée dans une transformation numérique ambitieuse à travers la **Stratégie Nationale de Développement du Numérique (SNNCI 2021-2025)**, structurée autour de 7 piliers stratégiques. Le pays ambitionne de devenir un **hub régional de la digitalisation** en Afrique de l'Ouest.

Dans ce cadre, le portail **data.gouv.ci** a été mis en place pour centraliser et diffuser les données publiques ivoiriennes. Il contient aujourd'hui **177 jeux de données publics** couvrant des domaines essentiels : démographie, éducation, énergie, santé, économie, environnement, télécommunications.

### 1.2 Le problème identifié

Malgré l'existence de ce portail et de son API REST publique, **trois obstacles majeurs** limitent l'exploitation de ces données :

**1. Inaccessibilité pour les agents IA**
Les outils d'Intelligence Artificielle modernes (agents conversationnels, assistants analytiques) ne peuvent pas interroger nativement les données gouvernementales ivoiriennes. Il n'existe aucun standard d'interfaçage entre les LLM (Large Language Models) et l'API data.gouv.ci.

**2. Absence d'interopérabilité**
Chaque ministère et organisme constitue un silo de données. Aucune infrastructure ne permet le croisement automatisé des datasets par des outils IA : croiser les données de déforestation avec les données économiques régionales, par exemple, nécessite aujourd'hui un travail manuel d'un data analyst.

**3. Potentiel IA inexploité**
La révolution des agents IA et des LLM offre des capacités analytiques sans précédent. En l'absence d'infrastructure MCP dédiée, ces capacités restent inaccessibles aux citoyens, chercheurs, journalistes et décideurs ivoiriens souhaitant exploiter les données publiques.

### 1.3 L'opportunité technologique

Le **Model Context Protocol (MCP)**, développé par Anthropic et adopté comme standard ouvert par l'industrie, est un protocole permettant aux agents IA d'interagir avec des sources de données externes de manière standardisée. En 2025-2026, tous les grands agents IA (Claude, ChatGPT, agents open source basés sur Llama/Qwen/Mistral) supportent ce protocole.

**opendata-civ-mcp** est la réponse à cette opportunité : le **premier serveur MCP connecté à un portail open data gouvernemental d'Afrique de l'Ouest**.

---

## 2. Présentation du projet

### 2.1 Définition

**opendata-civ-mcp** est un serveur Python implémentant le protocole MCP (Model Context Protocol) qui expose les données publiques du portail data.gouv.ci à tout agent IA compatible.

Il permet à un utilisateur de poser des questions en langage naturel sur les données publiques ivoiriennes et d'obtenir des analyses, visualisations et rapports générés automatiquement par un agent IA.

### 2.2 Exemple d'utilisation

```
Utilisateur : "Quelle est l'évolution de la déforestation 
               en Côte d'Ivoire depuis 2001 ?"

Agent IA     : [appelle search_datasets("déforestation CO2")]
               [appelle get_dataset_lines("perte-de-couverture-forestiere")]
               → Analyse : Entre 2001 et 2021, la Côte d'Ivoire a perdu 
                 3,46 Mha de couvert végétal (-23%), générant 1,71 Gt de CO₂.
                 Le pic de déforestation a été atteint en 2015-2016...
               [génère graphique d'évolution]
```

### 2.3 Caractère pionnier

À ce jour, **aucun pays de la zone UEMOA** ne dispose d'un MCP server connecté à son portail open data gouvernemental. Ce projet positionne la Côte d'Ivoire comme **précurseur continental** en matière d'intégration IA-données publiques.

---

## 3. Objectifs

### 3.1 Objectif principal

Construire et déployer un serveur MCP open source permettant à tout agent IA de requêter, analyser et croiser les 177 datasets publics du portail data.gouv.ci en langage naturel.

### 3.2 Objectifs spécifiques

| # | Objectif | Indicateur de succès |
|---|----------|----------------------|
| 1 | Exposer 100% des datasets publics via le protocole MCP | 177 datasets accessibles |
| 2 | Implémenter 5 outils MCP fonctionnels | 5 outils testés et documentés |
| 3 | Déployer une interface publique de démonstration | URL publique accessible |
| 4 | Publier le code en open source | Dépôt GitHub public |
| 5 | Documenter l'API pour les développeurs ivoiriens | Documentation complète |
| 6 | Supporter les modèles IA open source | Compatible Llama, Qwen, Mistral |

### 3.3 Objectifs à long terme

- Devenir l'infrastructure standard d'accès IA aux données publiques ivoiriennes
- Être répliqué dans d'autres pays de la CEDEAO
- Intégrer des datasets supplémentaires au fil des mises à jour du portail

---

## 4. Périmètre fonctionnel

### 4.1 Fonctionnalités incluses (V1)

#### Outil 1 — `search_datasets(query, topic?)`
**Description :** Recherche full-text dans le catalogue de datasets  
**Entrée :** Mots-clés de recherche, filtre thématique optionnel  
**Sortie :** Liste des datasets correspondants avec titre, description, nombre de lignes  
**Exemple :** `search_datasets("électricité rurale")` → 3 datasets trouvés

#### Outil 2 — `get_dataset_info(dataset_id)`
**Description :** Récupère les métadonnées complètes d'un dataset  
**Entrée :** Identifiant unique du dataset  
**Sortie :** Schéma des colonnes, période couverte, source, fréquence de mise à jour, licence  
**Exemple :** `get_dataset_info("bilan-electrification-rurale-2011-2023")`

#### Outil 3 — `get_dataset_lines(dataset_id, filters?)`
**Description :** Accède aux données réelles ligne par ligne  
**Entrée :** ID dataset, filtres optionnels (colonne, valeur, limite)  
**Sortie :** Données structurées en JSON prêtes pour analyse  
**Exemple :** `get_dataset_lines("echo-du-marche", {"ville": "Abidjan"})`

#### Outil 4 — `get_dataset_file(dataset_id, format?)`
**Description :** Génère un lien de téléchargement direct vers le fichier  
**Entrée :** ID dataset, format souhaité (CSV ou XLSX)  
**Sortie :** URL de téléchargement signée  
**Exemple :** `get_dataset_file("covid-civ", "csv")`

#### Outil 5 — `list_topics()`
**Description :** Liste toutes les thématiques disponibles avec le nombre de datasets  
**Entrée :** Aucune  
**Sortie :** Dictionnaire thématiques → nombre de datasets  
**Exemple :** `{"Éducation": 12, "Énergie": 8, "Démographie": 23, ...}`

### 4.2 Fonctionnalités exclues (V1 — à planifier en V2)

- Authentification des utilisateurs finaux
- Écriture ou mise à jour de datasets
- Analyse géospatiale avancée
- Tableaux de bord persistants
- Notifications temps réel sur les mises à jour de datasets

### 4.3 Données couvertes

Le portail data.gouv.ci couvre les thématiques suivantes, toutes accessibles via opendata-civ-mcp :

| Thématique | Datasets | Sources principales |
|------------|----------|---------------------|
| Démographie | 23 | ANStat, RGPH 2021 |
| Éducation | 18 | Ministère Éducation Nationale |
| Énergie & Électricité | 12 | CIE, Ministère Énergie |
| Environnement & Forêt | 4 | Global Forest Watch, Gouvernement |
| Économie & Budget | 10 | INS, BCEAO, Banque Mondiale |
| Santé | 9 | Ministère Santé |
| Transport | 8 | Ministère Transports |
| Télécommunications | 5 | ARTCI |
| Agriculture & Pêche | 12 | Ministère Agriculture |
| Société & Sécurité | 14 | ANStat, diverses |
| Tourisme | 4 | Ministère Tourisme |
| Autres | 58 | Diverses sources |

---

## 5. Architecture technique

### 5.1 Vue d'ensemble

```
┌─────────────────────────────────────────────────────────┐
│                    COUCHE PRÉSENTATION                   │
│         Interface Gradio (Hugging Face Spaces)           │
│              URL publique accessible                     │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                    COUCHE AGENT IA                       │
│   LLM Open Source (Llama 3.3-70B via Groq API)          │
│         Tool calling natif — MCP compatible              │
└─────────────────────┬───────────────────────────────────┘
                      │ Appels MCP
┌─────────────────────▼───────────────────────────────────┐
│            OPENDATA-CIV-MCP SERVER (Core)                 │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │search_dataset│  │get_dataset_  │  │get_dataset_   │  │
│  │s()           │  │info()        │  │lines()        │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                      │
│  │get_dataset_  │  │list_topics() │                      │
│  │file()        │  │              │                      │
│  └──────────────┘  └──────────────┘                      │
│                                                          │
│         Cache PostgreSQL / Redis (optionnel)             │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP / REST
┌─────────────────────▼───────────────────────────────────┐
│              API data.gouv.ci                            │
│    https://data.gouv.ci/data-fair/api/v1/catalog         │
│              177 datasets publics                        │
│         Licence Ouverte / Open Licence 2.0               │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Stack technologique

| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| Langage principal | Python 3.11+ | Maîtrise du porteur, écosystème data |
| Protocole MCP | SDK Anthropic MCP (`mcp` PyPI) | Standard officiel |
| LLM principal | Llama 3.3-70B (Groq API) | Open source, gratuit, tool calling |
| LLM alternatif | Qwen2.5-72B (Groq API) | Excellent en français |
| HTTP Client | `httpx` (async) | Performance, gestion des timeouts |
| Interface démo | Gradio | Déploiement Hugging Face Spaces |
| Cache | PostgreSQL | Réduction des appels API |
| Tests | `pytest` + `pytest-asyncio` | Couverture complète |
| CI/CD | GitHub Actions | Déploiement automatisé |
| Hébergement démo | Hugging Face Spaces | Gratuit, public, URL stable |

### 5.3 Standards et protocoles

- **MCP** (Model Context Protocol) — standard Anthropic, open source
- **OpenAPI 3.1** — documentation de l'API data.gouv.ci
- **DCAT** (Data Catalog Vocabulary) — format standard du catalogue
- **Licence Ouverte / Open Licence 2.0** — toutes les données sont librement réutilisables

---

## 6. Spécifications techniques détaillées

### 6.1 Structure du projet

```
opendata-civ-mcp/
├── src/
│   ├── server.py              # Point d'entrée MCP server
│   ├── tools/
│   │   ├── search.py          # search_datasets()
│   │   ├── dataset_info.py    # get_dataset_info()
│   │   ├── dataset_lines.py   # get_dataset_lines()
│   │   ├── dataset_file.py    # get_dataset_file()
│   │   └── topics.py          # list_topics()
│   ├── client/
│   │   └── datagouv_client.py # Client HTTP data.gouv.ci
│   └── cache/
│       └── postgres_cache.py  # Couche cache optionnelle
├── demo/
│   └── app.py                 # Interface Gradio
├── tests/
│   ├── test_tools.py
│   └── test_integration.py
├── docs/
│   ├── API.md
│   └── QUICKSTART.md
├── .env.example
├── requirements.txt
├── README.md
└── pyproject.toml
```

### 6.2 Spécifications des outils MCP

#### `search_datasets`

```python
@mcp.tool()
async def search_datasets(
    query: str,
    topic: str = None,
    size: int = 10
) -> list[dict]:
    """
    Recherche des jeux de données dans le portail open data 
    du gouvernement ivoirien (data.gouv.ci).
    
    Args:
        query: Mots-clés de recherche en français
        topic: Thématique optionnelle (Education, Energie, etc.)
        size: Nombre de résultats (max 50)
    
    Returns:
        Liste de datasets avec id, titre, description, 
        nombre de lignes, date de mise à jour
    """
```

#### `get_dataset_lines`

```python
@mcp.tool()
async def get_dataset_lines(
    dataset_id: str,
    filters: dict = None,
    limit: int = 100,
    select: list[str] = None
) -> dict:
    """
    Récupère les données réelles d'un jeu de données.
    
    Args:
        dataset_id: Identifiant unique du dataset
        filters: Filtres à appliquer {"colonne": "valeur"}
        limit: Nombre maximum de lignes (défaut 100, max 1000)
        select: Colonnes à retourner (toutes si None)
    
    Returns:
        {"total": int, "results": list[dict], "schema": list}
    """
```

### 6.3 Gestion des erreurs

Tous les outils implémentent une gestion d'erreurs robuste :

```python
class OpendataCivError(Exception):
    """Erreur de base opendata-civ-mcp"""

class DatasetNotFoundError(OpendataCivError):
    """Dataset introuvable sur data.gouv.ci"""

class APIRateLimitError(OpendataCivError):
    """Limite de taux API dépassée"""

class DataParsingError(OpendataCivError):
    """Erreur de parsing des données"""
```

### 6.4 Performance et cache

| Endpoint | TTL Cache | Stratégie |
|----------|-----------|-----------|
| `list_topics()` | 24h | Cache complet |
| `search_datasets()` | 1h | Cache par query hash |
| `get_dataset_info()` | 6h | Cache par dataset_id |
| `get_dataset_lines()` | 30min | Cache par (id + filtres) |
| `get_dataset_file()` | 6h | Redirect vers URL originale |

### 6.5 Sécurité

- Validation stricte des paramètres d'entrée (injection prevention)
- Rate limiting sur les appels sortants vers data.gouv.ci
- Pas de données sensibles stockées (toutes les données sont publiques)
- Logs d'accès sans données personnelles

---

## 7. Plan de développement

### 7.1 Phases du projet

#### Phase 1 — Fondations (Mois 1)
**Durée :** 4 semaines  
**Objectif :** Infrastructure de base fonctionnelle

- [ ] Audit complet des 177 datasets et de l'API data.gouv.ci
- [ ] Setup environnement de développement (Python, MCP SDK, Groq)
- [ ] Implémentation client HTTP data.gouv.ci avec gestion des erreurs
- [ ] Implémentation des outils `search_datasets()` et `list_topics()`
- [ ] Tests unitaires Phase 1

**Livrable :** Client API fonctionnel + 2 outils MCP testés

---

#### Phase 2 — Outils core (Mois 2)
**Durée :** 4 semaines  
**Objectif :** Les 5 outils MCP opérationnels

- [ ] Implémentation `get_dataset_info()`, `get_dataset_lines()`, `get_dataset_file()`
- [ ] Gestion des cas limites (datasets vides, encodage, pagination)
- [ ] Mise en place du cache PostgreSQL
- [ ] Tests d'intégration complets
- [ ] Compatibilité testée avec Llama 3.3-70B et Qwen2.5-72B

**Livrable :** Serveur MCP complet avec les 5 outils

---

#### Phase 3 — Interface démo (Mois 3-4)
**Durée :** 8 semaines  
**Objectif :** Démo publique accessible

- [ ] Développement interface Gradio avec chat conversationnel
- [ ] Déploiement sur Hugging Face Spaces
- [ ] Optimisation des prompts système pour le français ivoirien
- [ ] Sélection et mise en avant de 10 datasets prioritaires
- [ ] Documentation utilisateur complète

**Livrable :** URL publique de démonstration opérationnelle

---

#### Phase 4 — Validation & sécurité (Mois 5)
**Durée :** 4 semaines  
**Objectif :** Préparation production

- [ ] Tests de charge (simulations 100 requêtes simultanées)
- [ ] Audit de sécurité (validation inputs, rate limiting)
- [ ] Documentation technique complète (API.md, QUICKSTART.md)
- [ ] Guide d'intégration pour développeurs ivoiriens
- [ ] README en français et en anglais

**Livrable :** Code prêt pour contribution open source

---

#### Phase 5 — Présentation & financement (Mois 6)
**Durée :** 4 semaines  
**Objectif :** Obtenir le financement pour la V2

- [ ] Préparation pitch deck final
- [ ] Répétitions démo live
- [ ] Identification des partenaires techniques (ARTCI, ANStat)
- [ ] Rédaction dossier financement BAD / Banque Mondiale
- [ ] Présentation au Ministère de la Transition Numérique

**Livrable :** Dossier de financement V2 soumis

---

### 7.2 Tableau de bord du projet

```
Mois 1    Mois 2    Mois 3    Mois 4    Mois 5    Mois 6
  │         │         │         │         │         │
  ▼         ▼         ▼         ▼         ▼         ▼
Fondations  Outils   Interface  Interface  Sécurité  Pitch
  API       Core     Gradio     Démo       Tests     Ministère
  2 outils  5 outils Déploiement URL live  Doc       Financement
```

---

## 8. Livrables

### 8.1 Livrables techniques

| # | Livrable | Format | Échéance |
|---|----------|--------|----------|
| L1 | Code source complet | GitHub (open source) | Mois 4 |
| L2 | Serveur MCP fonctionnel | Package PyPI | Mois 4 |
| L3 | Interface de démonstration | Hugging Face Spaces | Mois 4 |
| L4 | Documentation technique | Markdown (docs/) | Mois 5 |
| L5 | Guide d'intégration développeurs | PDF + Markdown | Mois 5 |
| L6 | Suite de tests complète | pytest | Mois 5 |

### 8.2 Livrables non-techniques

| # | Livrable | Format | Échéance |
|---|----------|--------|----------|
| L7 | Rapport d'avancement mensuel | PDF | Chaque mois |
| L8 | Vidéo de démonstration | MP4 (5 min) | Mois 4 |
| L9 | Pitch deck ministère | PPTX | Mois 6 |
| L10 | Dossier financement V2 | PDF | Mois 6 |

---

## 9. Critères de succès

### 9.1 Critères techniques (obligatoires)

- [ ] Les 5 outils MCP répondent en moins de **3 secondes** en moyenne
- [ ] Taux de disponibilité de l'interface démo supérieur à **99%**
- [ ] **100% des 177 datasets** accessibles via les outils
- [ ] Compatibilité vérifiée avec **au moins 3 modèles IA** open source
- [ ] Couverture de tests supérieure à **80%**
- [ ] Zéro vulnérabilité de sécurité critique

### 9.2 Critères d'impact (souhaitables)

- [ ] **50+ développeurs** ayant cloné le dépôt GitHub dans les 3 mois post-lancement
- [ ] **10+ questions démo** fonctionnelles documentées en français
- [ ] **1 article ou mention** dans la presse tech africaine
- [ ] **1 partenariat** avec un organisme ivoirien (ARTCI, ANStat, ministère)

### 9.3 Critères de financement

- [ ] Présentation effectuée devant le Ministère de la Transition Numérique
- [ ] Dossier BAD/Banque Mondiale soumis
- [ ] Lettre d'intérêt d'au moins un partenaire institutionnel

---

## 10. Alignement stratégique SNNCI

Le projet opendata-civ-mcp s'inscrit directement dans **4 des 7 piliers** de la Stratégie Nationale de Développement du Numérique 2021-2025 :

### Pilier 2 — Services numériques ✅ (Impact direct)
> *"Dématérialisation des procédures, interopérabilité des systèmes"*

opendata-civ-mcp crée la première couche d'interopérabilité entre les données gouvernementales et les outils IA. Il s'inscrit dans la logique de la plateforme X-Road et du portail servicepublic.gouv.ci.

### Pilier 6 — Innovation ✅ (Impact direct)
> *"Stimuler l'innovation et les technologies émergentes (4RI)"*

Le projet implémente concrètement les technologies de la 4ème révolution industrielle (IA générative, agents autonomes) appliquées aux données publiques nationales. Il peut servir de catalyseur pour les startups ivoiriennes.

### Pilier 5 — Environnement des affaires ✅ (Impact indirect)
> *"Développer l'entrepreneuriat numérique"*

En publiant le code en open source et en documentant l'API pour les développeurs, le projet crée une infrastructure partagée réutilisable par les startups ivoiriennes pour construire de nouveaux services à valeur ajoutée.

### Pilier 1 — Infrastructures numériques ✅ (Impact indirect)
> *"Renforcement de la souveraineté numérique de l'État"*

L'utilisation de modèles open source (Llama, Qwen) et d'une infrastructure open source renforce la souveraineté numérique en évitant la dépendance exclusive à des fournisseurs propriétaires étrangers.

---

## 11. Budget prévisionnel

### 11.1 Coûts de développement

| Poste | Détail | Montant estimé |
|-------|--------|---------------|
| Développement (6 mois) | 1 ingénieur data senior | 18 000 000 FCFA |
| Infrastructure cloud | Hugging Face Pro, PostgreSQL managed | 600 000 FCFA |
| APIs et services | Groq API (usage), Anthropic API (tests) | 300 000 FCFA |
| Outils et licences | GitHub, monitoring, outils dev | 150 000 FCFA |
| Documentation & design | Traduction, mise en page docs | 300 000 FCFA |
| Déplacements & présentations | Transport, matériel démo | 500 000 FCFA |
| **Total V1** | | **19 850 000 FCFA** |

### 11.2 Coûts de la V2 (estimation, hors périmètre V1)

| Poste | Détail | Montant estimé |
|-------|--------|---------------|
| Développement V2 (12 mois) | 2-3 ingénieurs | 60 000 000 FCFA |
| Infrastructure production | Serveurs dédiés, haute disponibilité | 12 000 000 FCFA |
| Intégration ministères | APIs supplémentaires, partenariats | 8 000 000 FCFA |
| **Total V2** | | **~80 000 000 FCFA** |

> *Note : Le financement V2 est éligible aux programmes BAD (Banque Africaine de Développement) et Banque Mondiale dans le cadre du PARAE et du PRISDAGNE.*

---

## 12. Profil du porteur de projet

**Aboubakar Sidik MEITE**  
Ingénieur Data | Décisionnel & Data Warehouse

### Expériences pertinentes

**Ministère des Outre-mer — Paris** *(depuis septembre 2025)*
- Mise en place et exploitation de plateformes de données publiques (open data)
- Développement de pipelines de données automatisés
- Proof of Concept IA pour l'intégration analytique dans des tableaux de bord
- **→ Expérience directement transférable au contexte ivoirien**

**Mobilize Financial Services — Paris** *(jan. 2025 – sept. 2025)*
- Déploiement de pipelines Python analytiques sur Google Cloud Platform
- Conception de dashboards Power BI pour pilotage financier

**Renault Group — Villiers-Saint-Frédéric** *(sept. 2023 – jan. 2025)*
- Développement de 10+ dashboards Power BI
- Exploitation de données volumineuses via PySpark et SparkSQL

### Compétences clés pour ce projet

| Compétence | Niveau | Pertinence |
|------------|--------|------------|
| Python (API, async, httpx) | Expert | MCP Server core |
| Open data & APIs REST | Expert | Intégration data.gouv.ci |
| SQL & PostgreSQL | Avancé | Cache et stockage |
| Intelligence Artificielle | MBA en cours | Agent IA & LLM |
| Dataiku DSS | Certifié | Orchestration |
| Power BI | Certifié | Interface démo |

### Formation

- **MBA Intelligence Artificielle et Data** — Devinci Executive Education, Nanterre *(2025-en cours)*
- **Mastère Big Data** — IPSSI, Montigny-le-Bretonneux *(2023-2025)*
- **Licence Informatique** — Université de Versailles *(2020-2023)*

---

## 13. Risques et mesures d'atténuation

| # | Risque | Probabilité | Impact | Mesure d'atténuation |
|---|--------|-------------|--------|----------------------|
| R1 | API data.gouv.ci instable ou modifiée | Faible | Élevé | Versioning des appels, cache local, contact avec l'équipe technique |
| R2 | Changement de standard MCP | Très faible | Élevé | Abstraction de la couche MCP, suivi des releases Anthropic |
| R3 | Quota Groq API dépassé | Moyen | Moyen | Fallback sur Ollama local, gestion du rate limiting |
| R4 | Données sensibles exposées involontairement | Très faible | Très élevé | Toutes les données sont publiques sous Licence Ouverte 2.0 |
| R5 | Dépassement du budget temps (solo) | Moyen | Moyen | Scope V1 limité et réaliste, priorisation des 5 outils core |
| R6 | Faible adoption par les développeurs | Moyen | Faible | Documentation exemplaire, tutoriels vidéo, promotion via VITIB |

---

## 14. Glossaire

| Terme | Définition |
|-------|------------|
| **MCP** | Model Context Protocol — standard open source d'Anthropic permettant aux agents IA d'interagir avec des sources de données externes |
| **LLM** | Large Language Model — modèle de langage de grande taille (ex: Llama, Qwen, Claude) |
| **Tool calling** | Capacité d'un LLM à appeler des fonctions externes lors d'une conversation |
| **Open data** | Données publiques librement accessibles, réutilisables et redistribuables |
| **SNNCI** | Stratégie Nationale de Développement du Numérique de Côte d'Ivoire 2021-2025 |
| **DCAT** | Data Catalog Vocabulary — standard W3C pour la description de catalogues de données |
| **PARAE** | Projet d'Appui au Renforcement de l'Administration Électronique |
| **PRISDAGNE** | Programme de Renforcement des Infrastructures et Services Digitaux pour la Gouvernance Numérique de l'État |
| **BAD** | Banque Africaine de Développement |
| **ANStat** | Agence Nationale de la Statistique de Côte d'Ivoire |
| **ARTCI** | Autorité de Régulation des Télécommunications/TIC de Côte d'Ivoire |
| **PoC** | Proof of Concept — prototype démontrant la faisabilité d'un projet |
| **Groq** | Service cloud offrant un accès gratuit et ultra-rapide aux modèles IA open source |
| **Hugging Face Spaces** | Plateforme d'hébergement gratuit pour des applications IA interactives |

---

*Document rédigé par Aboubakar Sidik MEITE — Mai 2026*  
*Soumis au Ministère de la Transition Numérique et de la Digitalisation — République de Côte d'Ivoire*  
*contact : smeite20@gmail.com*
