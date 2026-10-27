"""
llm_router.py - Prompt-Aware Dynamic Model Router for Cache-Craft

Inspects prompt structure, intent, and domain (Code vs Deep Reasoning vs Fast Conversational)
and dynamically routes each query to the optimal model (local 7B/3B vs cloud) in <1 millisecond.
"""

import re
import time
import requests

OLLAMA_TAGS_URL = "http://127.0.0.1:11434/api/tags"

# In-memory cache for installed local models to avoid hitting Ollama API on every prompt
_installed_models_cache: list[str] = []
_installed_models_cached_at: float = 0.0
_CACHE_TTL_SECONDS = 15.0

# ─────────────────────────────────────────────────────────────────────────────
# Local Model Discovery & Availability
# ─────────────────────────────────────────────────────────────────────────────

def get_installed_ollama_models(force_refresh: bool = False) -> list[str]:
    """
    Returns list of installed Ollama models (e.g. ['llama3.2:latest', 'qwen2.5:7b']).
    Caches results for 15 seconds to ensure zero latency during high-frequency routing.
    """
    global _installed_models_cache, _installed_models_cached_at
    now = time.time()
    if not force_refresh and _installed_models_cache and (now - _installed_models_cached_at < _CACHE_TTL_SECONDS):
        return _installed_models_cache

    try:
        res = requests.get(OLLAMA_TAGS_URL, timeout=1.5)
        if res.status_code == 200:
            data = res.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            _installed_models_cache = models
            _installed_models_cached_at = now
            return models
    except Exception:
        pass

    # If Ollama is unreachable (e.g. running on cloud without local daemon), do not fake models
    return _installed_models_cache


def is_model_installed(target_id: str, installed_models: list[str] = None) -> bool:
    """Check if target_id or its prefix is currently installed in Ollama."""
    models = installed_models if installed_models is not None else get_installed_ollama_models()
    clean_target = target_id.lower().split(":")[0]
    for m in models:
        clean_m = m.lower().split(":")[0]
        if target_id.lower() in m.lower() or clean_target == clean_m:
            return True
    return False


def get_installed_model_exact_tag(target_id: str, installed_models: list[str] = None) -> str:
    """Return the exact tag of an installed model (e.g. 'qwen2.5:7b' or 'llama3.2:latest')."""
    models = installed_models if installed_models is not None else get_installed_ollama_models()
    clean_target = target_id.lower().split(":")[0]
    for m in models:
        clean_m = m.lower().split(":")[0]
        if target_id.lower() in m.lower() or clean_target == clean_m:
            return m
    return target_id


# ─────────────────────────────────────────────────────────────────────────────
# Prompt Intent Classification (< 1 millisecond execution)
# ─────────────────────────────────────────────────────────────────────────────

CODE_PATTERNS = [
    r"```[a-zA-Z]*",               # Code fences
    r"\b(def|class|function|const|let|var|import|from|export)\b",
    r"\b(return|async|await|lambda|yield|public|private|interface|struct)\b",
    r"\b(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE|JOIN|GROUP BY)\b",
    r"\b(dockerfile|docker-compose|kubectl|bash|powershell|regex|regexes)\b",
    r"\b(traceback|syntaxerror|nullpointerexception|exception|refactor)\b",
    r"\b(typescript|python|javascript|rust|golang|c\+\+|java|html|css|tailwind)\b",
    r"\b(api endpoint|fastapi|express|next\.js|react component|unit test)\b",
    r"\b(write code|write a script|write a function|implement an algorithm|debug this)\b",
    r"[{};()\[\]=><]{3,}",          # Multiple punctuation commonly in code snippets
]

REASONING_PATTERNS = [
    r"\b(step[-\s]?by[-\s]?step|chain[-\s]?of[-\s]?thought|think through)\b",
    r"\b(prove that|mathematical proof|calculate|derive|derivation|integral|derivative)\b",
    r"\b(why does|explain the mechanism|trade-off analysis|pros and cons of architecture)\b",
    r"\b(probability|bayesian|game theory|hypothesis|logical deduction|counter-example)\b",
    r"\b(compare and contrast|deep dive|analyze the root cause|formal logic)\b",
]

CONVERSATIONAL_GREETINGS = {
    "hello", "hi", "hey", "yo", "sup", "howdy", "greetings", "good morning",
    "good afternoon", "good evening", "how are you", "who are you", "what is your name",
    "what can you do", "help", "thanks", "thank you", "bye", "goodbye", "cool", "nice",
}


def classify_prompt(prompt: str) -> dict:
    """
    Classifies prompt intent in <1ms without any heavy network or LLM calls.
    Returns:
        {
            "category": "code" | "reasoning" | "conversational" | "general",
            "confidence": float,
            "reason": str,
        }
    """
    text = prompt.strip()
    words = text.split()
    word_count = len(words)
    lower = text.lower()

    # 1. Conversational / Quick Chit-Chat check
    if word_count <= 8 and (lower in CONVERSATIONAL_GREETINGS or any(lower.startswith(g) for g in CONVERSATIONAL_GREETINGS)):
        return {
            "category": "conversational",
            "confidence": 0.95,
            "reason": "Short conversational greeting / prompt -> routed for sub-second latency",
        }

    # 2. Code & Programming intent
    code_matches = sum(1 for pat in CODE_PATTERNS if re.search(pat, text, re.IGNORECASE))
    if code_matches >= 1 or "```" in text:
        confidence = min(0.99, 0.70 + (code_matches * 0.10))
        return {
            "category": "code",
            "confidence": confidence,
            "reason": f"Code syntax/keyword markers detected ({code_matches} pattern matches)",
        }

    # 3. Deep Analytical Reasoning & Mathematics
    reasoning_matches = sum(1 for pat in REASONING_PATTERNS if re.search(pat, text, re.IGNORECASE))
    if reasoning_matches >= 1:
        confidence = min(0.99, 0.70 + (reasoning_matches * 0.12))
        return {
            "category": "reasoning",
            "confidence": confidence,
            "reason": f"Analytical / mathematical reasoning intent detected ({reasoning_matches} pattern matches)",
        }

    # 4. Short simple definition queries (< 10 words)
    if word_count <= 10 and (lower.startswith("what is") or lower.startswith("who is") or lower.startswith("define ")):
        return {
            "category": "conversational",
            "confidence": 0.85,
            "reason": "Brief factual definition -> routed for lightweight fast response",
        }

    # 5. Default General Knowledge
    return {
        "category": "general",
        "confidence": 0.80,
        "reason": "General knowledge inquiry",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Dynamic Model Resolver
# ─────────────────────────────────────────────────────────────────────────────

def resolve_auto_model(
    prompt: str,
    force_offline: bool = False,
    circuit_breaker_active: bool = False
) -> tuple[str, str, str]:
    """
    Given a prompt and current environment state (offline mode, network breaker),
    dynamically selects the best installed model:

    - Code:        qwen2.5:7b (premier 7B coder) -> fallback llama3.1:8b -> llama3.2
    - Reasoning:   deepseek-r1:7b (chain-of-thought) -> qwen2.5:7b -> llama3.2
    - Short Chat:  llama3.2 (3B lightweight instant TTFT)
    - General:     gemini-flash-latest (if online) or qwen2.5:7b (if offline)

    Returns:
        (target_model_id, category, human_readable_reason)
    """
    classification = classify_prompt(prompt)
    category = classification["category"]
    installed = get_installed_ollama_models()

    is_offline = force_offline or circuit_breaker_active

    if category == "code":
        if is_model_installed("qwen2.5:7b", installed):
            target = get_installed_model_exact_tag("qwen2.5:7b", installed)
            return target, category, f"Coding domain detected -> dynamically routed to local {target} (optimal 7B coder)"
        elif is_model_installed("llama3.1:8b", installed):
            target = get_installed_model_exact_tag("llama3.1:8b", installed)
            return target, category, f"Coding domain detected -> dynamically routed to local {target}"
        elif is_model_installed("llama3.2", installed):
            target = get_installed_model_exact_tag("llama3.2", installed)
            return target, category, f"Coding domain detected -> routed to local {target} (Qwen 7B downloading)"
        else:
            return "gemini-3.6-flash", category, "Coding domain detected -> routed to Cloud Gemini"

    elif category == "reasoning":
        if is_model_installed("deepseek-r1:7b", installed):
            target = get_installed_model_exact_tag("deepseek-r1:7b", installed)
            return target, category, f"Deep analytical logic detected -> dynamically routed to local {target} (chain-of-thought)"
        elif is_model_installed("qwen2.5:7b", installed):
            target = get_installed_model_exact_tag("qwen2.5:7b", installed)
            return target, category, f"Complex reasoning detected -> dynamically routed to local {target} (high instruction precision)"
        elif is_offline and is_model_installed("llama3.2", installed):
            target = get_installed_model_exact_tag("llama3.2", installed)
            return target, category, f"Reasoning detected -> routed to local {target}"
        else:
            return "gemini-3.6-flash", category, "Complex multi-step reasoning -> routed to Gemini Flash Cloud"

    elif category == "conversational":
        if is_model_installed("llama3.2", installed):
            target = get_installed_model_exact_tag("llama3.2", installed)
            return target, category, f"Lightweight conversational query -> dynamically routed to local {target} (instant TTFT & low VRAM)"
        else:
            return "gemini-3.6-flash", category, "Conversational query -> routed to Gemini Flash"

    else:  # general
        if not is_offline:
            return "gemini-3.6-flash", category, "General knowledge query -> routed to high-speed Cloud Gemini"
        else:
            if is_model_installed("qwen2.5:7b", installed):
                target = get_installed_model_exact_tag("qwen2.5:7b", installed)
                return target, category, f"Offline Mode active -> routed to primary local flagship {target}"
            target = get_installed_model_exact_tag("llama3.2", installed)
            return target, category, f"Offline Mode active -> routed to local {target}"
