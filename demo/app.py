import json
import os
import sys
import asyncio
import time
from typing import Any
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
import streamlit as st
from cerebras.cloud.sdk import Cerebras, APIConnectionError, RateLimitError, APIStatusError

from src.tools import search_datasets, get_dataset_lines, get_dataset_info, list_topics, get_dataset_file

# ── Config ──────────────────────────────────────────────────────────────────
MODEL = "qwen-3-235b-a22b-instruct-2507"
client = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))

SYSTEM_PROMPT = """Tu es un assistant connecté exclusivement au portail open data officiel de Côte d'Ivoire — data.gouv.ci.

Tu as accès à 5 outils :
- list_topics : lister les thématiques disponibles
- search_datasets : rechercher des datasets par mots-clés
- get_dataset_info : obtenir le schéma d'un dataset avant d'en lire les données
- get_dataset_lines : lire les données réelles d'un dataset
- get_dataset_file : obtenir le lien de téléchargement CSV ou XLSX

Règles ABSOLUES :
1. Ne produis AUCUN chiffre, AUCUN tableau, AUCUNE statistique qui ne vienne pas d'un outil.
2. Séquence maximale : search_datasets → get_dataset_lines → RÉPONDRE. Pas plus de 3 appels d'outils par question.
3. Dès que tu as des données, rédige immédiatement ta réponse finale. Ne rappelle pas un outil si tu as déjà des données suffisantes.
4. Si après 1 recherche tu ne trouves rien, réponds directement : "Cette donnée n'est pas disponible sur data.gouv.ci." et propose des alternatives.
5. N'utilise JAMAIS tes connaissances d'entraînement pour produire des statistiques.
6. Réponds toujours en français avec des tableaux markdown si pertinent."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_topics",
            "description": "Liste toutes les thématiques disponibles sur data.gouv.ci avec le nombre de datasets par thématique.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_datasets",
            "description": "Recherche des jeux de données dans le portail open data du gouvernement ivoirien.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Mots-clés de recherche en français"},
                    "size": {"type": "integer", "description": "Nombre de résultats (défaut 10, max 50)", "default": 10},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_dataset_info",
            "description": "Récupère les métadonnées d'un dataset : colonnes, source, nombre de lignes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "slug": {"type": "string", "description": "Identifiant du dataset (obtenu via search_datasets)"}
                },
                "required": ["slug"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_dataset_lines",
            "description": "Récupère les données réelles d'un dataset.",
            "parameters": {
                "type": "object",
                "properties": {
                    "slug": {"type": "string", "description": "Identifiant du dataset"},
                    "limit": {"type": "integer", "description": "Nombre de lignes (défaut 100, max 1000)", "default": 100},
                    "filters": {"type": "object", "description": "Filtres {\"COLONNE\": \"valeur\"}"},
                },
                "required": ["slug"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_dataset_file",
            "description": "Retourne l'URL de téléchargement d'un dataset en CSV ou XLSX.",
            "parameters": {
                "type": "object",
                "properties": {
                    "slug": {"type": "string", "description": "Identifiant du dataset"},
                    "format": {"type": "string", "enum": ["csv", "xlsx"], "default": "csv"},
                },
                "required": ["slug"],
            },
        },
    },
]

EXAMPLES = [
    "Quelles thématiques de données sont disponibles ?",
    "Meilleurs lycées au Baccalauréat 2022",
    "Datasets sur l'énergie et l'électricité",
    "Télécharger les stats de l'enseignement primaire",
    "Évolution des effectifs scolaires 2010-2025",
]


# ── Outils (sync wrapper) ────────────────────────────────────────────────────
def run(coro):
    return asyncio.run(coro)


MAX_LINES = 50


def execute_tool(name: str, arguments: dict):
    try:
        if name == "list_topics":
            return run(list_topics())
        elif name == "search_datasets":
            return run(search_datasets(**arguments))
        elif name == "get_dataset_info":
            return run(get_dataset_info(**arguments))
        elif name == "get_dataset_lines":
            arguments["limit"] = min(arguments.get("limit", MAX_LINES), MAX_LINES)
            result = run(get_dataset_lines(**arguments))
            total = result.get("total", 0)
            if total > MAX_LINES:
                result["note"] = f"{total} lignes disponibles, {MAX_LINES} retournées. Utilise get_dataset_file pour télécharger l'ensemble."
            return result
        elif name == "get_dataset_file":
            return run(get_dataset_file(**arguments))
        return {"error": f"Outil inconnu : {name}"}
    except httpx.TimeoutException:
        return {"error": "Le portail data.gouv.ci ne répond pas (timeout). Réessayez dans quelques secondes."}
    except httpx.HTTPStatusError as e:
        return {"error": f"Erreur du portail data.gouv.ci (code {e.response.status_code})."}
    except Exception as e:
        return {"error": f"Erreur inattendue lors de l'appel à {name} : {str(e)}"}


# ── Boucle agentique ────────────────────────────────────────────────────────
def get_response(history: list, user_message: str) -> str:
    messages: list[Any] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    try:
        for _ in range(6):
            response: Any = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
                max_tokens=4096,
                temperature=0.3,
            )
            choice = response.choices[0]

            if choice.finish_reason == "tool_calls":
                tool_calls = choice.message.tool_calls or []
                serialized_calls = [
                    {"id": tc.id, "type": "function",
                     "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in tool_calls
                ]
                messages.append({
                    "role": "assistant",
                    "content": choice.message.content or "",
                    "tool_calls": serialized_calls,
                })
                for tc in tool_calls:
                    args = json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else {}
                    result = execute_tool(tc.function.name, args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result, ensure_ascii=False, default=str),
                    })
            else:
                return choice.message.content or ""

    except RateLimitError:
        time.sleep(12)
        try:
            response: Any = client.chat.completions.create(
                model=MODEL, messages=messages, tools=TOOLS, max_tokens=4096, temperature=0.3,
            )
            return response.choices[0].message.content or ""
        except Exception:
            raise RuntimeError("rate_limit")
    except APIConnectionError:
        raise RuntimeError("connection")
    except APIStatusError as e:
        raise RuntimeError(f"api_status:{e.status_code}")
    except Exception as e:
        raise RuntimeError(f"generic:{str(e)}")

    return "Désolé, je n'ai pas pu terminer l'analyse. Veuillez reformuler votre question."


APP_PASSWORD = os.environ.get("APP_PASSWORD", "")


def check_password() -> bool:
    if st.session_state.get("authenticated"):
        return True

    st.markdown("""
    <div style="display:flex;height:4px;width:100%;">
        <div style="flex:1;background:#006B3C;"></div>
        <div style="flex:1;background:#E8EAED;"></div>
        <div style="flex:1;background:#D4600A;"></div>
    </div>
    <div style="padding:32px 0 24px 0;border-bottom:1px solid #EBEBEB;margin-bottom:32px;">
        <div style="font-size:18px;font-weight:700;color:#111827;margin-bottom:4px;">
            Données Publiques — Côte d'Ivoire
        </div>
        <div style="font-size:13px;color:#6B7280;">Accès restreint</div>
    </div>
    """, unsafe_allow_html=True)

    pwd = st.text_input("Mot de passe", type="password", placeholder="Entrez le mot de passe d'accès")

    if st.button("Accéder", type="primary"):
        if pwd == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.markdown(
                "<div style='background:#FEF2F2;border:1px solid #FECACA;border-left:3px solid #DC2626;"
                "border-radius:6px;padding:10px 14px;color:#991B1B;font-size:13px;margin-top:8px;'>"
                "Mot de passe incorrect.</div>",
                unsafe_allow_html=True,
            )
    return False


# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Données Publiques — Côte d'Ivoire",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer, .stDeployButton { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }

.stApp {
    background: #FFFFFF;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
}
.block-container {
    padding-top: 0 !important;
    padding-bottom: 40px !important;
    max-width: 780px !important;
}

/* Input container */
[data-testid="stChatInput"] {
    border: 1.5px solid #D4600A !important;
    border-radius: 8px !important;
    background: #FFFFFF !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #D4600A !important;
    box-shadow: none !important;
    outline: none !important;
}
[data-testid="stChatInput"] textarea {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    font-size: 14px !important;
    font-family: 'Segoe UI', system-ui, sans-serif !important;
    color: #111827 !important;
    background: transparent !important;
}
[data-testid="stChatInput"] textarea:focus {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] button[kind="primaryFormSubmit"] {
    background: #D4600A !important;
    border-radius: 6px !important;
}
[data-testid="stChatInput"] button[kind="primaryFormSubmit"]:hover {
    background: #B85209 !important;
}

/* Messages */
[data-testid="stChatMessage"] {
    background: transparent !important;
    padding: 4px 0 !important;
}

/* Exemples */
div[data-testid="stButton"] button {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 6px !important;
    color: #374151 !important;
    font-size: 13px !important;
    text-align: left !important;
    width: 100% !important;
    padding: 8px 14px !important;
    transition: all 0.15s !important;
    font-family: 'Segoe UI', system-ui, sans-serif !important;
}
div[data-testid="stButton"] button:hover {
    border-color: #D4600A !important;
    color: #D4600A !important;
    background: #FFF8F4 !important;
}

/* Spinner */
[data-testid="stSpinner"] p {
    font-size: 13px !important;
    color: #6B7280 !important;
}
</style>
""", unsafe_allow_html=True)

if not check_password():
    st.stop()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;height:4px;width:100%;margin-bottom:0;">
    <div style="flex:1;background:#006B3C;"></div>
    <div style="flex:1;background:#E8EAED;"></div>
    <div style="flex:1;background:#D4600A;"></div>
</div>
<div style="padding:24px 0 18px 0;border-bottom:1px solid #EBEBEB;margin-bottom:24px;">
    <div style="font-size:18px;font-weight:700;color:#111827;letter-spacing:-0.3px;margin-bottom:4px;">
        Données Publiques : Côte d'Ivoire
    </div>
    <div style="font-size:13px;color:#6B7280;margin-bottom:14px;">
        Interrogez les données officielles de data.gouv.ci en langage naturel
    </div>
    <div style="display:flex;gap:20px;flex-wrap:wrap;">
        <span style="font-size:12px;color:#6B7280;display:flex;align-items:center;gap:6px;">
            <span style="width:6px;height:6px;border-radius:50%;background:#006B3C;display:inline-block;flex-shrink:0;"></span>177 jeux de données
        </span>
        <span style="font-size:12px;color:#6B7280;display:flex;align-items:center;gap:6px;">
            <span style="width:6px;height:6px;border-radius:50%;background:#006B3C;display:inline-block;flex-shrink:0;"></span>data.gouv.ci
        </span>
        <span style="font-size:12px;color:#6B7280;display:flex;align-items:center;gap:6px;">
            <span style="width:6px;height:6px;border-radius:50%;background:#D4600A;display:inline-block;flex-shrink:0;"></span>Recherche · Analyse · Export CSV/XLSX
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Session state ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending" not in st.session_state:
    st.session_state.pending = None

# ── Exemples (affichés uniquement si chat vide) ──────────────────────────────
if not st.session_state.messages:
    st.markdown(
        "<div style='font-size:12px;font-weight:600;color:#9CA3AF;letter-spacing:0.5px;"
        "text-transform:uppercase;margin-bottom:10px;'>Questions fréquentes</div>"
        "<div style='height:2px;background:#D4600A;border-radius:2px;margin-bottom:14px;'></div>",
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for i, example in enumerate(EXAMPLES):
        with cols[i % 2]:
            if st.button(example, key=f"ex_{i}"):
                st.session_state.pending = example
                st.rerun()
    st.markdown("<div style='margin-bottom:24px;'></div>", unsafe_allow_html=True)

# ── Historique du chat ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Traitement du message ────────────────────────────────────────────────────
ERROR_MESSAGES = {
    "rate_limit": (
        "Le service est temporairement surchargé. "
        "Veuillez patienter quelques secondes avant de réessayer."
    ),
    "connection": (
        "Impossible de joindre le service d'analyse. "
        "Vérifiez votre connexion internet et réessayez."
    ),
}

def _error_html(message: str) -> str:
    return (
        f"<div style='background:#FEF2F2;border:1px solid #FECACA;border-left:3px solid #DC2626;"
        f"border-radius:6px;padding:12px 16px;color:#7F1D1D;font-size:13px;line-height:1.6;'>"
        f"<strong style='display:block;margin-bottom:4px;color:#991B1B;'>Une erreur est survenue</strong>"
        f"{message}</div>"
    )

def handle_message(user_input: str):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyse en cours..."):
            try:
                reply = get_response(st.session_state.messages[:-1], user_input)
                st.markdown(reply)
            except RuntimeError as e:
                err = str(e)
                if err == "rate_limit":
                    msg = ERROR_MESSAGES["rate_limit"]
                    st.toast("Service surchargé — réessayez dans quelques secondes.", icon="⏳")
                elif err == "connection":
                    msg = ERROR_MESSAGES["connection"]
                    st.toast("Connexion impossible au service d'analyse.", icon="🔌")
                elif err.startswith("api_status:"):
                    code = err.split(":")[1]
                    msg = f"Le service d'analyse a retourné une erreur (code {code}). Réessayez dans quelques instants."
                    st.toast(f"Erreur API ({code}).", icon="⚠️")
                else:
                    msg = "Une erreur inattendue s'est produite. Réessayez ou reformulez votre question."
                    st.toast("Erreur inattendue.", icon="⚠️")
                reply = ""
                st.markdown(_error_html(msg), unsafe_allow_html=True)

    if reply:
        st.session_state.messages.append({"role": "assistant", "content": reply})

# Exemple cliqué
if st.session_state.pending:
    pending = st.session_state.pending
    st.session_state.pending = None
    handle_message(pending)
    st.rerun()

# Saisie manuelle
if user_input := st.chat_input("Posez votre question sur les données ivoiriennes..."):
    handle_message(user_input)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;font-size:11px;color:#9CA3AF;padding:24px 0 8px 0;
border-top:1px solid #F3F4F6;margin-top:16px;">
    Données issues de
    <a href="https://data.gouv.ci" target="_blank"
       style="color:#006B3C;text-decoration:none;font-weight:500;">data.gouv.ci</a>
    &nbsp;·&nbsp; Projet open source <strong>opendata-civ-mcp</strong>
    &nbsp;·&nbsp; Licence Ouverte 2.0
</div>
""", unsafe_allow_html=True)
