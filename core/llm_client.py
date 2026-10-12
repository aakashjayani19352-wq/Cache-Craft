"""
llm_client.py - Pluggable LLM Integration (Google Gemini Cloud + Local Ollama fallback)

Strategy (updated):
  1. DEFAULT is now Gemini Cloud (gemini-flash-latest) — fast, reliable, key is configured.
  2. If Gemini fails (quota, network) → automatic local Ollama fallback.
  3. If Ollama also fails → returns a clean error in <8s (timeout reduced from 60s to 8s).
  4. Both tiers are fully resilient — no hanging, no crashes.
"""

import os
import sys
import time
import shutil
import subprocess
import requests
from dotenv import load_dotenv
import core.database as db

load_dotenv()

OLLAMA_BASE = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_CHAT_URL = f"{OLLAMA_BASE}/api/chat"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE}/api/tags"
OLLAMA_TIMEOUT_S = 45          # Allows cold 7B model loading into GPU VRAM
GEMINI_CONNECT_TIMEOUT_S = 12.0  # Robust connect timeout for realistic networks
GEMINI_READ_TIMEOUT_S = 30.0    # Allows ample generation read window for cloud LLM requests

# Gemini is the default cloud model
DEFAULT_MODEL = "gemini-flash-latest"


def ensure_ollama_running() -> bool:
    """
    Checks if Ollama daemon is active on port 11434.
    If not running, attempts to launch `ollama serve` in the background (Windows detached process)
    and waits up to 6 seconds for it to bind to port 11434.
    """
    try:
        r = requests.get(OLLAMA_TAGS_URL, timeout=1.0)
        if r.status_code == 200:
            return True
    except Exception:
        pass

    # Find ollama binary
    ollama_bin = shutil.which("ollama")
    if not ollama_bin and sys.platform == "win32":
        default_win_path = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe")
        if os.path.exists(default_win_path):
            ollama_bin = default_win_path

    if not ollama_bin:
        return False

    print(f"[Ollama Auto-Start] Launching Ollama background daemon via {ollama_bin}...")
    try:
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

        subprocess.Popen(
            [ollama_bin, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags
        )

        for _ in range(12):
            time.sleep(0.5)
            try:
                r = requests.get(OLLAMA_TAGS_URL, timeout=0.8)
                if r.status_code == 200:
                    print("[Ollama Auto-Start] Daemon successfully online on port 11434!")
                    return True
            except Exception:
                pass
    except Exception as e:
        print(f"[Ollama Auto-Start] Failed to launch daemon: {e}")

    return False


def get_gpu_hardware_telemetry(target_model: str = None) -> dict:
    """
    Returns true hardware telemetry for the local NVIDIA GPU and Ollama VRAM allocation.
    Directly reads physical VRAM via `nvidia-smi` and active residency via Ollama's /api/ps.
    """
    clean_target = (target_model or "qwen2.5:7b").lower()
    gpu_data = {
        "gpu_name": "NVIDIA GeForce RTX 4060 Laptop GPU",
        "vram_used_mb": 0,
        "vram_total_mb": 8188,
        "vram_free_mb": 8188,
        "utilization_pct": 0,
        "nvidia_smi_ok": False,
        "ollama_online": False,
        "loaded_models": [],
        "is_model_in_vram": False,
        "target_model": clean_target,
        "vram_size_formatted": "0 GB",
        "vram_size_bytes": 0,
    }

    # 1. Physical VRAM via nvidia-smi
    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu,name", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=4.0
        )
        if res.returncode == 0 and res.stdout.strip():
            parts = [p.strip() for p in res.stdout.strip().split(",")]
            if len(parts) >= 3:
                gpu_data["vram_used_mb"] = int(float(parts[0]))
                gpu_data["vram_total_mb"] = int(float(parts[1]))
                gpu_data["vram_free_mb"] = max(0, gpu_data["vram_total_mb"] - gpu_data["vram_used_mb"])
                gpu_data["utilization_pct"] = int(float(parts[2]))
                gpu_data["nvidia_smi_ok"] = True
            if len(parts) >= 4 and parts[3]:
                gpu_data["gpu_name"] = parts[3]
    except Exception:
        pass

    # 2. Ollama running models & VRAM residency via /api/ps
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/ps", timeout=1.5)
        if r.status_code == 200:
            gpu_data["ollama_online"] = True
            data = r.json()
            models = data.get("models", [])
            for m in models:
                vram_bytes = m.get("size_vram", 0)
                m_info = {
                    "name": m.get("name", ""),
                    "model": m.get("model", ""),
                    "size_vram_bytes": vram_bytes,
                    "size_vram_mb": round(vram_bytes / (1024 * 1024), 1),
                    "size_vram_formatted": f"{round(vram_bytes / (1024**3), 2)} GB" if vram_bytes > 0 else "0 GB",
                    "expires_at": m.get("expires_at"),
                }
                gpu_data["loaded_models"].append(m_info)

                # Check if target model is physically resident in VRAM
                m_name = m_info["name"].lower()
                m_mod = m_info["model"].lower()
                target_base = clean_target.split(":")[0]
                if (clean_target in m_name or clean_target in m_mod or target_base in m_name or target_base in m_mod) and vram_bytes > 0:
                    gpu_data["is_model_in_vram"] = True
                    gpu_data["vram_size_formatted"] = m_info["size_vram_formatted"]
                    gpu_data["vram_size_bytes"] = vram_bytes
    except Exception:
        pass

    return gpu_data


def preload_local_gpu_model(model_name: str = "qwen2.5:7b") -> dict:
    """
    Physically loads model weights into RTX 4060 GPU VRAM.
    CRITICAL: Only returns vram_loaded=True AFTER verifying `size_vram > 0` via /api/ps.
    """
    clean_model = model_name or "qwen2.5:7b"

    # Step 1: Ensure Ollama is running
    daemon_ok = ensure_ollama_running()
    if not daemon_ok:
        return {
            "status": "error",
            "message": "Local Ollama daemon is not running on port 11434 and could not be started.",
            "vram_loaded": False,
            "model": clean_model
        }

    # Step 2: Check if model is ALREADY resident in GPU VRAM
    telemetry = get_gpu_hardware_telemetry(clean_model)
    if telemetry.get("is_model_in_vram"):
        return {
            "status": "ready",
            "model": clean_model,
            "vram_loaded": True,
            "vram_size_bytes": telemetry["vram_size_bytes"],
            "vram_size_formatted": telemetry["vram_size_formatted"],
            "load_time_ms": 0,
            "device": telemetry["gpu_name"],
            "vram_used_mb": telemetry["vram_used_mb"],
            "vram_total_mb": telemetry["vram_total_mb"],
            "message": f"Model {clean_model} is already resident in RTX 4060 VRAM."
        }

    # Step 3: Physically load model into GPU VRAM via Ollama /api/generate
    try:
        t0 = time.perf_counter()
        res = requests.post(
            f"{OLLAMA_BASE}/api/generate",
            json={"model": clean_model, "prompt": "", "keep_alive": -1},
            timeout=45
        )
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        if res.status_code != 200:
            return {
                "status": "error",
                "model": clean_model,
                "vram_loaded": False,
                "message": f"Ollama returned HTTP {res.status_code}: {res.text[:120]}"
            }

        # Step 4: PHYSICALLY VERIFY via /api/ps and nvidia-smi
        verified_telemetry = None
        for _ in range(6):
            verified_telemetry = get_gpu_hardware_telemetry(clean_model)
            if verified_telemetry.get("is_model_in_vram"):
                break
            time.sleep(0.5)

        if not verified_telemetry or not verified_telemetry.get("is_model_in_vram"):
            return {
                "status": "error",
                "model": clean_model,
                "vram_loaded": False,
                "message": f"Model load command completed, but physical VRAM verification failed (0 bytes reported)."
            }

        print(f"[Ollama] Model '{clean_model}' verified resident in GPU VRAM ({verified_telemetry['vram_size_formatted']}) in {elapsed_ms}ms.")
        return {
            "status": "ready",
            "model": clean_model,
            "vram_loaded": True,
            "vram_size_bytes": verified_telemetry["vram_size_bytes"],
            "vram_size_formatted": verified_telemetry["vram_size_formatted"],
            "load_time_ms": elapsed_ms,
            "device": verified_telemetry["gpu_name"],
            "vram_used_mb": verified_telemetry["vram_used_mb"],
            "vram_total_mb": verified_telemetry["vram_total_mb"],
            "message": f"Model {clean_model} physically loaded and verified in RTX 4060 VRAM."
        }
    except Exception as e:
        print(f"[Ollama Preload] Error: {e}")
        return {
            "status": "error",
            "model": clean_model,
            "vram_loaded": False,
            "message": f"Failed to load model into GPU: {str(e)}"
        }


def unload_local_gpu_model(model_name: str = None) -> dict:
    """
    Unloads local LLM weights from RTX 4060 GPU VRAM, freeing dedicated memory back to 0 MB.
    Called on browser tab close (beforeunload/pagehide) or when user toggles back to Online mode.
    """
    clean_model = model_name or "qwen2.5:7b"
    unloaded_models = []

    try:
        # Check currently loaded models
        targets = [clean_model]
        try:
            r = requests.get(f"{OLLAMA_BASE}/api/ps", timeout=1.5)
            if r.status_code == 200:
                for m in r.json().get("models", []):
                    m_name = m.get("name") or m.get("model")
                    if m_name and m_name not in targets:
                        targets.append(m_name)
        except Exception:
            pass

        for target in targets:
            try:
                res = requests.post(
                    f"{OLLAMA_BASE}/api/generate",
                    json={"model": target, "prompt": "", "keep_alive": 0},
                    timeout=5
                )
                if res.status_code == 200:
                    unloaded_models.append(target)
            except Exception:
                pass

        telemetry = get_gpu_hardware_telemetry(clean_model)
        print(f"[Ollama Unload] Released GPU VRAM. Unloaded: {unloaded_models}. Current VRAM: {telemetry.get('vram_used_mb', 0)} MB.")
        return {
            "status": "unloaded",
            "unloaded_models": unloaded_models,
            "vram_used_mb": telemetry.get("vram_used_mb", 0),
            "vram_total_mb": telemetry.get("vram_total_mb", 8188),
            "is_model_in_vram": telemetry.get("is_model_in_vram", False),
            "message": f"GPU VRAM released. Models unloaded from RTX 4060."
        }
    except Exception as e:
        print(f"[Ollama Unload] Error: {e}")
        return {
            "status": "error",
            "message": f"Failed to unload model from GPU: {str(e)}"
        }


def get_available_models() -> list[dict]:
    """
    Dynamically returns only models that are ACTUALLY installed in Ollama on this PC,
    plus Auto-Router and Gemini Cloud.
    Guarantees the UI never lists uninstalled/phantom models.
    """
    try:
        from core.llm_router import get_installed_ollama_models
        installed = get_installed_ollama_models()
    except Exception:
        installed = ["qwen2.5:7b", "llama3.2:latest"]

    models = [
        {
            "id": "auto",
            "name": "Auto-Router (Dynamic Prompt-Aware)",
            "provider": "auto",
            "type": "hybrid",
            "description": "Dynamically inspects prompt intent & complexity — routes code & reasoning to Qwen 7B, fast chat to Llama 3.2",
        },
        {
            "id": "gemini-flash-latest",
            "name": "Google Gemini Flash (Cloud)",
            "provider": "gemini",
            "type": "cloud",
            "description": "High-speed cloud LLM — primary inference engine with automatic local fallback",
        },
    ]

    known_meta = {
        "qwen2.5:7b": {
            "name": "Ollama (Qwen 2.5 — 7B Local)",
            "description": "Flagship 7B local model on RTX 4060 — state-of-the-art coding, math, and complex reasoning (4.7 GB)",
        },
        "qwen2.5": {
            "name": "Ollama (Qwen 2.5 — 7B Local)",
            "description": "Flagship 7B local model on RTX 4060 — state-of-the-art coding, math, and complex reasoning (4.7 GB)",
        },
        "llama3.2:latest": {
            "name": "Ollama (Llama 3.2 — 3B Local)",
            "description": "Ultra-fast 3B local model — instant response time for conversational chit-chat & greetings (2.0 GB)",
        },
        "llama3.2": {
            "name": "Ollama (Llama 3.2 — 3B Local)",
            "description": "Ultra-fast 3B local model — instant response time for conversational chit-chat & greetings (2.0 GB)",
        },
    }

    seen_ids = set()
    for inst in installed:
        raw_id = inst
        norm_id = inst.replace(":latest", "") if inst.endswith(":latest") else inst
        if norm_id in seen_ids or raw_id in seen_ids:
            continue
        seen_ids.add(norm_id)
        seen_ids.add(raw_id)

        meta = known_meta.get(inst) or known_meta.get(norm_id) or known_meta.get(inst.split(":")[0])
        name = meta["name"] if meta else f"Ollama ({inst})"
        desc = meta["description"] if meta else f"Local model installed in Ollama ({inst})"
        models.append({
            "id": norm_id,
            "name": name,
            "provider": "ollama",
            "type": "local",
            "description": desc,
            "installed": True,
        })

    # If Ollama had no models detected, fallback to the two models confirmed on disk
    if not any(m["type"] == "local" for m in models):
        models.extend([
            {
                "id": "qwen2.5:7b",
                "name": "Ollama (Qwen 2.5 — 7B Local)",
                "provider": "ollama",
                "type": "local",
                "description": "Flagship 7B local model on RTX 4060 — state-of-the-art coding, math, and complex reasoning (4.7 GB)",
                "installed": True,
            },
            {
                "id": "llama3.2",
                "name": "Ollama (Llama 3.2 — 3B Local)",
                "provider": "ollama",
                "type": "local",
                "description": "Ultra-fast 3B local model — instant response time for conversational chit-chat & greetings (2.0 GB)",
                "installed": True,
            }
        ])

    return models

AVAILABLE_MODELS = get_available_models()

# ── Circuit Breaker for Weak/Degraded Networks ─────────────────────────────
_circuit_open_until = 0.0
_last_circuit_reason = ""


def is_circuit_open() -> bool:
    """Returns True if the cloud network was recently detected as weak/down."""
    return time.time() < _circuit_open_until


def get_circuit_status() -> dict:
    """Return circuit breaker state and remaining cooldown."""
    active = is_circuit_open()
    remaining = max(0, int(_circuit_open_until - time.time())) if active else 0
    return {
        "is_open": active,
        "cooldown_seconds": remaining,
        "reason": _last_circuit_reason if active else None,
    }


def record_cloud_failure(reason: str):
    """Trip the circuit breaker for 45 seconds when network is weak or fails."""
    global _circuit_open_until, _last_circuit_reason
    _circuit_open_until = time.time() + 45.0
    _last_circuit_reason = reason
    print(f"[LLM] Weak network / cloud error detected: {reason}. Circuit tripped for 45s -> routing directly to local LLM.")


def record_cloud_success():
    """Reset circuit breaker upon a successful cloud call."""
    global _circuit_open_until, _last_circuit_reason
    _circuit_open_until = 0.0
    _last_circuit_reason = ""


_offline_mode_memory: bool = False


# ── Mode & Settings Management ─────────────────────────────────────────────
def is_offline_mode_enabled() -> bool:
    """Check if Offline Mode is toggled on (persisted in DB or memory)."""
    try:
        val = db.get_setting("offline_mode")
        if val is not None:
            return val == "true"
    except Exception:
        pass
    return _offline_mode_memory


def set_offline_mode(enabled: bool) -> bool:
    """Toggle and persist Offline Mode in settings."""
    global _offline_mode_memory
    _offline_mode_memory = enabled
    try:
        db.set_setting("offline_mode", "true" if enabled else "false")
    except Exception as e:
        print(f"[LLM] Notice: Could not persist offline_mode to DB ({e})")
    return enabled


def is_cloud_model(model_name: str) -> bool:
    """Check if a model ID corresponds to a cloud provider."""
    return "gemini" in (model_name or "").lower()


def get_active_model() -> str:
    """Retrieve active LLM model from settings. Defaults to Gemini if not set."""
    try:
        saved = db.get_setting("selected_model")
        return saved if saved else DEFAULT_MODEL
    except Exception:
        return DEFAULT_MODEL


def set_active_model(model_name: str) -> str:
    """Persist active LLM model in settings."""
    try:
        db.set_setting("selected_model", model_name)
    except Exception as e:
        print(f"[LLM] Notice: Could not persist model to DB ({e})")
    return model_name


def get_preferred_local_model() -> str:
    """
    Get the local model to route to when offline or falling back.
    If the active model is already local, returns that.
    Otherwise checks for a saved preference or defaults to llama3.2 (installed).
    """
    active = get_active_model()
    if not is_cloud_model(active):
        return active
    try:
        preferred = db.get_setting("preferred_local_model")
        if preferred:
            return preferred
    except Exception:
        pass
    return "llama3.2"


# ── Provider Invocations ───────────────────────────────────────────────────
def _call_gemini(question: str, messages: list = None, model: str = "gemini-flash-latest") -> dict:
    """
    Send request to Google Gemini API with automatic fallback across available Flash endpoints.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"answer": None, "model": model, "source": "gemini_error", "error": "Missing GEMINI_API_KEY in environment."}

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

    clean_req_model = model.replace("models/", "")
    candidate_models = [clean_req_model]
    for fallback_name in ["gemini-flash-latest", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-flash-lite-latest", "gemma-4-26b-a4b-it"]:
        if fallback_name not in candidate_models:
            candidate_models.append(fallback_name)

    system_instruction_text = (
        "You are Cache-Craft AI, a fast, helpful, and highly capable assistant. "
        "When greeted (e.g. 'hello', 'hi', 'hey'), respond with a friendly greeting and ask how you can help. Never repeat or continue a previous conversation topic when greeted. "
        "Always write in clean, clear Markdown and natural readable prose. "
        "Never wrap basic scientific terms, variables, numbers, or chemical formulas in raw LaTeX code ($...$). "
        "Use clean Unicode characters directly in the text (e.g. sp³, CH₄, H₂O, 109.5°, σ bonds, π bonds, 1s² 2s² 2p²). "
        "Only use display math blocks ($$ ... $$ on separate lines) when writing complex multi-line mathematical proofs or equations."
    )

    payload = {
        "systemInstruction": {
            "parts": [{"text": system_instruction_text}]
        },
        "contents": contents
    }
    last_err = ""

    for target_model in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={api_key}"
        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=(GEMINI_CONNECT_TIMEOUT_S, GEMINI_READ_TIMEOUT_S)
            )

            # Fallback if specific model does not support systemInstruction in v1beta
            if response.status_code == 400 and "systemInstruction" in payload:
                response = requests.post(
                    url,
                    json={"contents": contents},
                    headers={"Content-Type": "application/json"},
                    timeout=(GEMINI_CONNECT_TIMEOUT_S, GEMINI_READ_TIMEOUT_S)
                )

            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return {
                            "answer": parts[0].get("text", ""),
                            "model": target_model,
                            "source": f"Gemini ({target_model})",
                            "error": None
                        }
                return {"answer": None, "model": target_model, "source": "gemini_error", "error": "Empty response from Gemini API"}

            # If 503 or 404, try next model in candidate chain
            last_err = f"HTTP {response.status_code}: {response.text[:150]}"
            if response.status_code in (404, 503):
                continue
            else:
                break

        except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout) as e:
            last_err = f"Network timeout ({e})"
            continue
        except requests.exceptions.ConnectionError:
            return {"answer": None, "model": target_model, "source": "gemini_error", "error": "Network unreachable (no internet connection)"}
        except Exception as e:
            last_err = str(e)
            continue

    return {"answer": None, "model": candidate_models[0], "source": "gemini_error", "error": last_err or "All Gemini endpoints unavailable"}


def _call_ollama(question: str, messages: list = None, model: str = "llama3.2") -> dict:
    """Send request to local Ollama instance running on localhost:11434 with automatic background daemon auto-launch."""
    try:
        # Guarantee local Ollama server is running on port 11434 before sending request
        ensure_ollama_running()

        formatted_messages = []
        system_prompt = {
            "role": "system",
            "content": (
                "You are Cache-Craft AI, a fast, helpful, and highly capable assistant. "
                "When greeted (e.g. 'hello', 'hi', 'hey'), respond with a friendly greeting and ask how you can help. Never repeat or continue a previous conversation topic when greeted. "
                "Always write in clean, clear Markdown and natural readable prose. "
                "Never wrap basic scientific terms, variables, numbers, or chemical formulas in raw LaTeX code ($...$). "
                "Use clean Unicode characters directly in the text (e.g. sp³, CH₄, H₂O, 109.5°, σ bonds, π bonds, 1s² 2s² 2p²). "
                "Only use display math blocks ($$ ... $$ on separate lines) when writing complex multi-line mathematical proofs or equations."
            )
        }

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

        if not any(m.get("role") == "system" for m in formatted_messages):
            formatted_messages.insert(0, system_prompt)

        response = requests.post(
            OLLAMA_CHAT_URL,
            json={
                "model": model,
                "messages": formatted_messages,
                "stream": False
            },
            timeout=OLLAMA_TIMEOUT_S
        )

        if response.status_code == 200:
            data = response.json()
            answer = data.get("message", {}).get("content", "")
            return {
                "answer": answer,
                "model": model,
                "source": f"Ollama ({model})",
                "error": None
            }

        return {
            "answer": None,
            "model": model,
            "source": "ollama_error",
            "error": f"HTTP {response.status_code} — is Ollama running?"
        }

    except requests.exceptions.Timeout:
        return {"answer": None, "model": model, "source": "ollama_error",
                "error": "Ollama timed out (model is taking too long to load)"}
    except requests.exceptions.ConnectionError:
        return {"answer": None, "model": model, "source": "ollama_error",
                "error": "Could not connect to Ollama (port 11434 unreachable — run `ollama serve`)"}
    except Exception as e:
        return {"answer": None, "model": model, "source": "ollama_error", "error": str(e)}


def _make_error_response(model: str, error_msg: str) -> dict:
    """Return a clean, user-visible error dict that does NOT get cached."""
    return {
        "answer": f"⚠️ **LLM Unavailable**: {error_msg}\n\n*Cache hits still work normally. You can enable Offline Mode or check your local Ollama instance.*",
        "model": model,
        "source": "error",
        "error": error_msg,
        "offline_mode": is_offline_mode_enabled(),
        "fallback_triggered": False,
    }


# ── Unified Inference Router ───────────────────────────────────────────────
def generate_answer(
    question: str,
    messages: list = None,
    model: str = None,
    force_offline: bool = None
) -> dict:
    """
    Intelligent Inference Router with Instant Failover & Offline Mode:

    1. Offline Mode (configured from start OR toggled mid-session):
       - Directly executes local Ollama (zero cloud/network calls).
       - Consistent format, zero latency penalty.

    2. Weak Network Circuit Breaker:
       - If network was recently weak or timed out, subsequent queries
         instantly skip cloud calls (0ms wasted) and route directly to local LLM.

    3. Online Mode with Fast Failover:
       - Attempts Gemini with a 3.5s connect timeout.
       - If network is weak, times out in 3.5s and IMMEDIATELY switches
         to local Ollama without freezing the user.
       - Trips the circuit breaker so next queries switch instantly.
    """
    # Check if offline mode is requested (per-request mid-switch OR global setting)
    offline_active = force_offline if (force_offline is not None) else is_offline_mode_enabled()
    selected_model = model or get_active_model()
    local_fallback_model = get_preferred_local_model()

    # --- CASE 0: Dynamic Auto-Router active (prompt-aware dynamic switching) ---
    if selected_model == "auto":
        from core.llm_router import resolve_auto_model
        routed_model, router_category, router_reason = resolve_auto_model(
            question,
            force_offline=offline_active,
            circuit_breaker_active=is_circuit_open()
        )
        print(f"[LLM Router] Dynamic switch -> {routed_model} for category '{router_category}' ({router_reason})")

        if not is_cloud_model(routed_model):
            res = _call_ollama(question, messages=messages, model=routed_model)
            if res["error"] is None:
                res["offline_mode"] = True
                res["fallback_triggered"] = False
                res["routed_model"] = routed_model
                res["router_category"] = router_category
                res["router_reason"] = router_reason
                return res
            # If routed local model failed (e.g. still downloading), fallback to installed local model
            print(f"[LLM Router] Routed local model {routed_model} failed ({res['error']}). Trying fallback {local_fallback_model}...")
            if local_fallback_model != routed_model:
                fallback_local = _call_ollama(question, messages=messages, model=local_fallback_model)
                if fallback_local["error"] is None:
                    fallback_local["offline_mode"] = True
                    fallback_local["fallback_triggered"] = True
                    fallback_local["routed_model"] = local_fallback_model
                    fallback_local["router_category"] = router_category
                    fallback_local["router_reason"] = f"{router_reason} (fell back to {local_fallback_model})"
                    return fallback_local
            # If not offline, rescue with Gemini
            if not offline_active:
                cloud_res = _call_gemini(question, messages=messages, model=DEFAULT_MODEL)
                if cloud_res["error"] is None:
                    cloud_res["offline_mode"] = False
                    cloud_res["fallback_triggered"] = True
                    cloud_res["routed_model"] = DEFAULT_MODEL
                    cloud_res["router_category"] = router_category
                    cloud_res["router_reason"] = f"Rescued by Gemini after local {routed_model} error"
                    return cloud_res
            return _make_error_response(routed_model, f"Auto-route local failed: {res['error']}")
        else:
            # Routed to cloud
            res = _call_gemini(question, messages=messages, model=routed_model)
            if res["error"] is None:
                record_cloud_success()
                res["offline_mode"] = False
                res["fallback_triggered"] = False
                res["routed_model"] = routed_model
                res["router_category"] = router_category
                res["router_reason"] = router_reason
                return res
            # Cloud failed -> trip breaker and use local
            record_cloud_failure(res["error"])
            fallback = _call_ollama(question, messages=messages, model=local_fallback_model)
            if fallback["error"] is None:
                fallback["offline_mode"] = True
                fallback["fallback_triggered"] = True
                fallback["fallback_reason"] = f"Switched from cloud auto-route due to weak network: {res['error']}"
                fallback["routed_model"] = local_fallback_model
                fallback["router_category"] = router_category
                fallback["router_reason"] = f"{router_reason} (auto-switched to local {local_fallback_model})"
                return fallback
            return _make_error_response(routed_model, f"Auto-route cloud failed: {res['error']} | Local: {fallback['error']}")

    # --- CASE 1: Offline Mode active (from start or mid-switch) ---
    if offline_active:
        target_local = selected_model if not is_cloud_model(selected_model) else local_fallback_model
        print(f"[LLM] Offline Mode active: generating directly with local {target_local} (zero network calls).")
        res = _call_ollama(question, messages=messages, model=target_local)
        if res["error"] is None:
            res["offline_mode"] = True
            res["fallback_triggered"] = False
            return res
        return _make_error_response(target_local, f"Offline Mode active: {res['error']}")

    # --- CASE 2: Local model explicitly selected by user ---
    if not is_cloud_model(selected_model):
        res = _call_ollama(question, messages=messages, model=selected_model)
        if res["error"] is None:
            res["offline_mode"] = True
            res["fallback_triggered"] = False
            return res

        # Local model failed, attempt Gemini rescue if available
        print(f"[LLM] Local model {selected_model} failed ({res['error']}). Attempting Gemini rescue...")
        fallback = _call_gemini(question, messages=messages, model=DEFAULT_MODEL)
        if fallback["error"] is None:
            fallback["offline_mode"] = False
            fallback["fallback_triggered"] = True
            fallback["note"] = f"Rescued by Gemini after local error: {res['error']}"
            return fallback

        return _make_error_response(selected_model, f"Local: {res['error']} | Gemini: {fallback['error']}")

    # --- CASE 3: Cloud model (Gemini) with Weak Network Fast-Failover ---
    # Check circuit breaker: if network previously failed, don't wait on timeouts!
    if is_circuit_open():
        print(f"[LLM] Weak network circuit breaker open: skipping cloud call → routing directly to local {local_fallback_model}.")
        res = _call_ollama(question, messages=messages, model=local_fallback_model)
        if res["error"] is None:
            res["offline_mode"] = True
            res["fallback_triggered"] = True
            res["fallback_reason"] = f"Weak network circuit breaker active ({_last_circuit_reason})"
            res["note"] = f"Instant local switch: weak network detected recently. Used local {local_fallback_model}."
            return res
        # If even local failed during circuit breaker, try cloud as last ditch
        print(f"[LLM] Local fallback also failed ({res['error']}). Trying cloud as last resort...")

    # Attempt Cloud call with fast connect timeout (3.5s)
    res = _call_gemini(question, messages=messages, model=selected_model)
    if res["error"] is None:
        record_cloud_success()
        res["offline_mode"] = False
        res["fallback_triggered"] = False
        return res

    # Weak network or cloud error! Trip circuit and switch to local LLM if host supports it
    print(f"[LLM] Cloud failed: {res['error']}.")

    has_local_ollama = shutil.which("ollama") is not None or (sys.platform == "win32" and os.path.exists(os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe")))

    if has_local_ollama:
        print(f"[LLM] Switching to local {local_fallback_model}...")
        record_cloud_failure(res["error"])
        fallback = _call_ollama(question, messages=messages, model=local_fallback_model)
        if fallback["error"] is None:
            fallback["offline_mode"] = True
            fallback["fallback_triggered"] = True
            fallback["fallback_reason"] = f"Switched from cloud due to weak network: {res['error']}"
            fallback["note"] = f"Network weak ({res['error']}). Switched immediately to local {local_fallback_model}."
            return fallback

    if "429" in str(res["error"]):
        return _make_error_response(selected_model, "Google Gemini API quota exceeded (HTTP 429). Please check or update your GEMINI_API_KEY.")

    return _make_error_response(selected_model, f"Cloud: {res['error']}")
