"""
llm_client.py - Pluggable LLM Integration (Local Ollama + Google Gemini Cloud)

Supports:
- Local Ollama: llama3.2 (default, 100% offline)
- Google Gemini Cloud API: gemini-3.8-flash (via GEMINI_API_KEY)
- Seamless fallback: If Gemini API encounters errors/limits, automatically falls back to local Ollama.
"""

import os
import requests
from dotenv import load_dotenv
import core.database as db

load_dotenv()

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3.2"

AVAILABLE_MODELS = [
    {
        "id": "llama3.2",
        "name": "Ollama (llama3.2 — 3B Local)",
        "provider": "ollama",
        "type": "local",
        "description": "Fast, private, 100% offline local inference",
    },
    {
        "id": "gemini-3.8-flash",
        "name": "Google Gemini 3.8 Flash (Cloud)",
        "provider": "gemini",
        "type": "cloud",
        "description": "High-speed cloud LLM with automatic local fallback",
    }
]


def get_active_model() -> str:
    """Retrieve active LLM model from settings or default to llama3.2."""
    saved = db.get_setting("selected_model")
    return saved if saved else DEFAULT_MODEL


def set_active_model(model_name: str) -> str:
    """Persist active LLM model in settings."""
    db.set_setting("selected_model", model_name)
    return model_name


def _call_gemini(question: str, messages: list = None, model: str = "gemini-3.8-flash") -> dict:
    """Send request to Google Gemini API via official REST endpoint."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"error": "Missing GEMINI_API_KEY in environment variables."}

    clean_model = model.replace("models/", "")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={api_key}"

    contents = []
    if messages and len(messages) > 0:
        for m in messages[-20:]:
            role = "user" if m.get("role") == "user" else "model"
            content = m.get("content", "").strip()
            if content:
                contents.append({"role": role, "parts": [{"text": content}]})

        if not contents or contents[-1].get("role") != "user":
            contents.append({"role": "user", "parts": [{"text": question}]})
    else:
        contents = [{"role": "user", "parts": [{"text": question}]}]

    response = requests.post(
        url,
        json={"contents": contents},
        headers={"Content-Type": "application/json"},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                return {
                    "answer": parts[0].get("text", ""),
                    "model": clean_model,
                    "source": f"cloud_gemini ({clean_model})",
                    "error": None
                }
        return {"error": "Empty response from Gemini API"}
    else:
        return {"error": f"HTTP {response.status_code}: {response.text[:200]}"}


def _call_ollama(question: str, messages: list = None, model: str = "llama3.2") -> dict:
    """Send request to local Ollama instance."""
    try:
        formatted_messages = []
        if messages and len(messages) > 0:
            for m in messages:
                role = m.get("role", "user")
                content = m.get("content", "")
                if role in ("user", "assistant", "system") and content:
                    formatted_messages.append({"role": role, "content": content})

            if not formatted_messages or formatted_messages[-1].get("content") != question:
                formatted_messages.append({"role": "user", "content": question})

            if len(formatted_messages) > 20:
                formatted_messages = formatted_messages[-20:]
        else:
            formatted_messages = [{"role": "user", "content": question}]

        response = requests.post(
            OLLAMA_CHAT_URL,
            json={
                "model": model,
                "messages": formatted_messages,
                "stream": False
            },
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            answer = data.get("message", {}).get("content", "")
            return {
                "answer": answer,
                "model": model,
                "source": "local_llm",
                "error": None
            }

        return {
            "answer": f"[Local LLM Error] HTTP {response.status_code}. Is Ollama running?",
            "model": model,
            "source": "local_llm_error",
            "error": f"HTTP {response.status_code}"
        }

    except requests.exceptions.ConnectionError:
        return {
            "answer": "[Local LLM Error] Could not connect to Ollama. Please run 'ollama serve'.",
            "model": model,
            "source": "local_llm_error",
            "error": "ConnectionError"
        }
    except Exception as e:
        return {
            "answer": f"[Local LLM Error] {str(e)}",
            "model": model,
            "source": "local_llm_error",
            "error": str(e)
        }


def generate_answer(question: str, messages: list = None, model: str = None) -> dict:
    """
    Pluggable generation with automatic cloud-to-local fallback:
    1. If model is Gemini (or active model is Gemini), tries Gemini Cloud API.
    2. If Gemini is unavailable, rate-limited, or fails, gracefully falls back to local Ollama.
    """
    selected_model = model or get_active_model()

    if "gemini" in selected_model.lower():
        res = _call_gemini(question, messages=messages, model=selected_model)
        if not res.get("error"):
            return res

        # Graceful fallback to local Ollama
        print(f"[LLM Client] Gemini call failed ({res.get('error')}). Falling back to local Ollama (llama3.2)...")
        fallback = _call_ollama(question, messages=messages, model="llama3.2")
        fallback["note"] = f"Fell back from {selected_model} due to cloud error: {res.get('error')}"
        return fallback

    # Default: Local Ollama
    return _call_ollama(question, messages=messages, model=selected_model)
