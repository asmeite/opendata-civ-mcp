import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
from cerebras.cloud.sdk import AsyncCerebras

from src.tools.search import search_datasets
from src.tools.dataset_lines import get_dataset_lines
from src.tools.dataset_info import get_dataset_info
from src.tools.topics import list_topics
from src.tools.dataset_file import get_dataset_file

MODEL = "qwen-3-235b-a22b-instruct-2507"

client = AsyncCerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))

SYSTEM_PROMPT = """Tu es un assistant expert en données publiques de Côte d'Ivoire, connecté au portail officiel data.gouv.ci.

Tu as accès à 5 outils pour explorer et analyser ces données :
- list_topics : découvrir les thématiques disponibles (à appeler en premier si l'utilisateur explore)
- search_datasets : rechercher des datasets par mots-clés
- get_dataset_info : obtenir le schéma et les métadonnées d'un dataset avant d'en lire les données
- get_dataset_lines : lire les données réelles d'un dataset (avec filtres optionnels)
- get_dataset_file : obtenir le lien de téléchargement CSV ou XLSX d'un dataset

Règles :
- Réponds toujours en français
- Sois analytique : cite les chiffres clés, compare, explique les tendances
- Utilise des tableaux markdown quand les données s'y prêtent
- Si une question nécessite plusieurs datasets, enchaîne les appels d'outils
- Ne fais jamais de suppositions sur les données : appelle toujours un outil pour les obtenir"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_topics",
            "description": "Liste toutes les thématiques disponibles sur data.gouv.ci avec le nombre de datasets par thématique. À appeler en premier pour découvrir ce qui existe.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_datasets",
            "description": "Recherche des jeux de données dans le portail open data du gouvernement ivoirien (data.gouv.ci).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Mots-clés de recherche en français (ex: 'électricité', 'éducation BAC', 'déforestation')",
                    },
                    "size": {
                        "type": "integer",
                        "description": "Nombre de résultats à retourner (défaut 10, max 50)",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_dataset_info",
            "description": "Récupère les métadonnées complètes d'un dataset : colonnes disponibles, source, nombre de lignes, valeurs possibles. À appeler avant get_dataset_lines pour connaître les colonnes filtrables.",
            "parameters": {
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Identifiant unique du dataset (obtenu via search_datasets)",
                    }
                },
                "required": ["slug"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_dataset_lines",
            "description": "Récupère les données réelles d'un dataset ligne par ligne.",
            "parameters": {
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Identifiant unique du dataset",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Nombre de lignes à retourner (défaut 100, max 1000)",
                        "default": 100,
                    },
                    "filters": {
                        "type": "object",
                        "description": "Filtres optionnels {\"COLONNE\": \"valeur\"} (ex: {\"DREN\": \"Abidjan 1\"})",
                    },
                },
                "required": ["slug"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_dataset_file",
            "description": "Retourne l'URL de téléchargement direct d'un dataset en CSV ou XLSX.",
            "parameters": {
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Identifiant unique du dataset",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["csv", "xlsx"],
                        "description": "Format souhaité (défaut: csv)",
                        "default": "csv",
                    },
                },
                "required": ["slug"],
            },
        },
    },
]


async def _execute_tool(name: str, arguments: dict):
    if name == "list_topics":
        return await list_topics()
    elif name == "search_datasets":
        return await search_datasets(**arguments)
    elif name == "get_dataset_info":
        return await get_dataset_info(**arguments)
    elif name == "get_dataset_lines":
        return await get_dataset_lines(**arguments)
    elif name == "get_dataset_file":
        return await get_dataset_file(**arguments)
    return {"error": f"Outil inconnu : {name}"}


async def respond(message: str, history: list):
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    for item in history:
        if isinstance(item, dict):
            messages.append({"role": item["role"], "content": item["content"]})
        else:
            user_msg, assistant_msg = item
            messages.append({"role": "user", "content": user_msg})
            if assistant_msg:
                messages.append({"role": "assistant", "content": assistant_msg})

    messages.append({"role": "user", "content": message})

    for _ in range(10):
        response = await client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            max_tokens=4096,
            temperature=0.3,
        )
        choice = response.choices[0]

        if choice.finish_reason == "tool_calls":
            tool_calls = choice.message.tool_calls or []
            messages.append({
                "role": "assistant",
                "content": choice.message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in tool_calls
                ],
            })
            for tc in tool_calls:
                args = (
                    json.loads(tc.function.arguments)
                    if isinstance(tc.function.arguments, str)
                    else tc.function.arguments or {}
                )
                result = await _execute_tool(tc.function.name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result, ensure_ascii=False, default=str),
                })
        else:
            return choice.message.content or ""

    return "Désolé, je n'ai pas pu terminer l'analyse. Veuillez reformuler votre question."


demo = gr.ChatInterface(
    fn=respond,
   # type="messages",
    title="🇨🇮 Assistant Données Publiques — data.gouv.ci",
    description=(
        "Posez vos questions sur les données publiques de Côte d'Ivoire. "
        "Je recherche, analyse et télécharge des datasets depuis [data.gouv.ci](https://data.gouv.ci)."
    ),
    examples=[
        "Quelles thématiques de données sont disponibles sur data.gouv.ci ?",
        "Montre-moi les meilleurs lycées au Baccalauréat 2022",
        "Quels datasets existent sur l'énergie et l'électricité ?",
        "Donne-moi le lien pour télécharger les statistiques de l'enseignement primaire",
        "Compare le taux de réussite au BAC 2022 entre les établissements publics et privés",
    ],
    chatbot=gr.Chatbot(height=520),
    textbox=gr.Textbox(placeholder="Ex: Quelles sont les régions avec le plus d'élèves inscrits au BAC ?", scale=7),
)

if __name__ == "__main__":
    demo.launch()
