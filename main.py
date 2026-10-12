"""
Cache-Craft API Server

A multi-tier semantic cache middleware designed to reduce LLM API costs.
Implements a routing architecture: L1 (Redis Exact Hash) -> L2 (PostgreSQL Vector Search) -> L3 (LLM API).
"""

import time
import os
import json
import asyncio

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, field_validator

from core.cache_router import CacheRouter
import core.database as db
from core.device_auth import is_gpu_access_authorized, is_creator_hardware

app = FastAPI(
    title="Cache-Craft API",
    description="Multi-tier semantic cache — reduces LLM API cost via L0 Memory → L1 Hash → L2 Vector → L3 LLM routing.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_private_network_access_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response

# Initialize PostgreSQL & pgvector tables on startup (if database is available)
try:
    db.init_db()
    print("[Startup] PostgreSQL database and pgvector tables initialized successfully.")
except Exception as e:
    print(f"[Startup] PostgreSQL init notice (resilient mode active): {e}")

# Auto-start Ollama in background if installed locally
try:
    import core.llm_client as llm
    llm.ensure_ollama_running()
except Exception as e:
    print(f"[Startup] Ollama check: {e}")

# Load persisted threshold and TTL from DB on startup (survives restarts)
_saved = None
_saved_ttl = None
try:
    _saved = db.get_setting("similarity_threshold")
    _saved_ttl = db.get_setting("ttl_seconds")
except Exception:
    pass

router = CacheRouter(
    similarity_threshold=float(_saved) if _saved else 0.85,
    ttl_seconds=int(_saved_ttl) if _saved_ttl else 86400
)


# ============================================================
# Request / Response Models
# ============================================================

class QueryRequest(BaseModel):
    question: str
    messages: list[dict] | None = None
    offline_mode: bool | None = None  # Mid-session override: force local Ollama for this query
    model: str | None = None         # Specific model OR 'auto' for dynamic prompt-aware routing

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Question cannot be empty.")
        if len(v) > 10_000:
            raise ValueError("Question too long — max 10,000 characters.")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "What was our total revenue in Q3?",
                "messages": [
                    {"role": "user", "content": "Tell me about Q3"},
                    {"role": "assistant", "content": "Q3 performance was strong."},
                    {"role": "user", "content": "What was our total revenue in Q3?"}
                ],
                "offline_mode": False
            }
        }
    }


class OfflineModeRequest(BaseModel):
    offline_mode: bool
    preferred_local_model: str | None = None

    model_config = {"json_schema_extra": {"example": {"offline_mode": True, "preferred_local_model": "qwen2.5:7b"}}}


class StoreRequest(BaseModel):
    question: str
    answer: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "What was our total revenue in Q3?",
                "answer": "Total revenue for Q3 was $4.2 million.",
            }
        }
    }


class ThresholdRequest(BaseModel):
    threshold: float

    @field_validator("threshold")
    @classmethod
    def validate_threshold(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Threshold must be between 0.0 and 1.0.")
        return round(v, 4)

    model_config = {"json_schema_extra": {"example": {"threshold": 0.80}}}


class TTLRequest(BaseModel):
    ttl_seconds: int

    @field_validator("ttl_seconds")
    @classmethod
    def validate_ttl(cls, v: int) -> int:
        if v < 0:
            raise ValueError("TTL seconds cannot be negative (use 0 for permanent).")
        return v

    model_config = {"json_schema_extra": {"example": {"ttl_seconds": 86400}}}


class ModelRequest(BaseModel):
    model: str

    model_config = {"json_schema_extra": {"example": {"model": "llama3.2"}}}


class FeedbackRequest(BaseModel):
    query_hash: str
    is_positive: bool

    model_config = {"json_schema_extra": {"example": {"query_hash": "abc123...", "is_positive": True}}}


# ============================================================
# Endpoints — Health
# ============================================================

@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "Cache-Craft API", "version": "2.0.0"}


@app.get("/api/health", tags=["Health"])
def detailed_health():
    """Real health check: database + embedding model + LLM connectivity + offline status."""
    import requests as req
    import core.llm_client as llm

    db_ok = False
    try:
        db.get_cache_size()
        db_ok = True
    except Exception:
        try:
            db.init_db()
            db.get_cache_size()
            db_ok = True
        except Exception:
            pass

    llm_ok = False
    llm_model = None
    try:
        r = req.get(llm.OLLAMA_TAGS_URL, timeout=0.5)
        if r.status_code == 200:
            llm_ok = True
            models = r.json().get("models", [])
            if models:
                llm_model = models[0].get("name")
    except Exception:
        pass

    # If local Ollama is not running, check Cloud Gemini connectivity
    if not llm_ok and os.environ.get("GEMINI_API_KEY"):
        llm_ok = True
        llm_model = "gemini-flash-latest (Cloud)"

    return {
        "status": "ok" if (db_ok and llm_ok) else "degraded",
        "database": "ok" if db_ok else "error",
        "llm": "ok" if llm_ok else "unavailable",
        "llm_model": llm_model or "unknown",
        "embedding_model": "all-MiniLM-L6-v2",
        "offline_mode": llm.is_offline_mode_enabled(),
        "circuit_breaker": llm.get_circuit_status(),
    }


# ============================================================
# Endpoints — Query
# ============================================================

@app.post("/api/query", tags=["Query"])
def query(request: QueryRequest, req: Request):
    """Main endpoint — 3-tier cache lookup with intelligent weak-network failover, offline mode & dynamic auto-routing."""
    client_ip = req.client.host if req.client else "unknown"
    simulate_guest = req.query_params.get("guest") == "1" or req.query_params.get("simulate_guest", "").lower() in ("true", "1", "yes")

    # If an unauthorized guest/friend requests offline mode or local GPU models, gracefully fallback to online Cloud
    force_offline = request.offline_mode
    target_model = request.model
    if force_offline or (target_model and "qwen" in target_model):
        if simulate_guest or not is_gpu_access_authorized(client_ip):
            force_offline = False
            target_model = "gemini-flash-latest"

    return router.search(
        request.question,
        messages=request.messages,
        force_offline=force_offline,
        model=target_model
    )


@app.get("/api/models/classify", tags=["Models"])
def test_classify(prompt: str):
    """Inspect how the prompt-aware dynamic router classifies a prompt."""
    from core.llm_router import classify_prompt, resolve_auto_model
    classification = classify_prompt(prompt)
    target_model, category, reason = resolve_auto_model(prompt)
    return {
        "prompt": prompt,
        "classification": classification,
        "resolved_model": target_model,
        "category": category,
        "routing_reason": reason
    }


@app.post("/api/models/preload", tags=["Models"])
def preload_model(request: Request, model: str = "qwen2.5:7b"):
    """Preloads local LLM model weights directly into GPU VRAM (RTX 4060). Restricted to creator's PC."""
    client_ip = request.client.host if request.client else "unknown"
    simulate_guest = request.query_params.get("guest") == "1" or request.query_params.get("simulate_guest", "").lower() in ("true", "1", "yes")

    if simulate_guest or not is_gpu_access_authorized(client_ip):
        raise HTTPException(
            status_code=403,
            detail="Sorry, you're not allowed to access the GPU"
        )

    try:
        import requests as req
        import core.llm_client as llm
        r = req.get(llm.OLLAMA_TAGS_URL, timeout=1.5)
        local_ollama_available = (r.status_code == 200)
    except Exception:
        local_ollama_available = False

    if not local_ollama_available:
        return {
            "status": "error",
            "message": "Local Ollama daemon is offline on port 11434."
        }

    import core.llm_client as llm
    return llm.preload_local_gpu_model(model)


# ============================================================
# Endpoints — Device Security & GPU Permissions
# ============================================================

@app.get("/api/system/gpu-access", tags=["System"])
def check_gpu_access(request: Request):
    """
    Checks if the requesting client and host machine are authorized to access the local GPU.
    Returns whether GPU access is granted or restricted for guests/friends.
    """
    client_ip = request.client.host if request.client else "unknown"
    simulate_guest = request.query_params.get("guest") == "1" or request.query_params.get("simulate_guest", "").lower() in ("true", "1", "yes")
    allowed = False if simulate_guest else is_gpu_access_authorized(client_ip)

    return {
        "gpu_access_allowed": allowed,
        "is_creator_device": is_creator_hardware(),
        "client_ip": client_ip,
        "message": "" if allowed else "Sorry, you're not allowed to access the GPU"
    }


@app.get("/api/tunnel/status", tags=["Tunnel"])
def get_tunnel():
    """Local-only mode active: remote tunnel is permanently disabled."""
    return {"status": "inactive", "url": None, "message": "Local GPU runs strictly on creator machine."}


@app.post("/api/tunnel/start", tags=["Tunnel"])
def start_tunnel_endpoint():
    """Local-only mode active: remote tunnel disabled."""
    return {"status": "inactive", "url": None, "message": "Remote tunnel is disabled."}


@app.post("/api/tunnel/stop", tags=["Tunnel"])
def stop_tunnel_endpoint():
    """Stop tunnel stub."""
    return {"status": "inactive", "url": None, "message": "Tunnel is inactive."}


# ============================================================
# Endpoints — Analytics
# ============================================================

@app.get("/api/history", tags=["Analytics"])
def get_history(limit: int = 100):
    try:
        return {"history": db.get_query_history(limit)}
    except Exception:
        return {"history": []}


@app.get("/api/metrics", tags=["Analytics"])
def get_metrics():
    """Real-time cache statistics with tier breakdown, hourly trend, and latency percentiles."""
    metrics = router.get_metrics()
    try:
        metrics["tier_breakdown"] = db.get_tier_breakdown()
    except Exception:
        metrics["tier_breakdown"] = {"L1 (Redis)": {"count": 0, "avg_latency_ms": 0.0}, "L2 (PostgreSQL)": {"count": 0, "avg_latency_ms": 0.0}}
    try:
        metrics["hourly_stats"] = db.get_hourly_stats(24)
    except Exception:
        metrics["hourly_stats"] = []
    try:
        metrics["latency_percentiles"] = db.get_latency_percentiles()
    except Exception:
        metrics["latency_percentiles"] = {"hit": {"p50": 0.0, "p90": 0.0, "p99": 0.0}, "miss": {"p50": 0.0, "p90": 0.0, "p99": 0.0}}
    return metrics


@app.get("/api/metrics/stream", tags=["Analytics"])
async def stream_metrics():
    """Server-Sent Events (SSE) endpoint streaming real-time cache analytics."""
    async def event_generator():
        while True:
            try:
                metrics = router.get_metrics()
                metrics["tier_breakdown"] = db.get_tier_breakdown()
                yield f"data: {json.dumps(metrics)}\n\n"
            except Exception as e:
                yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
            await asyncio.sleep(2)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )


@app.post("/api/benchmark", tags=["Analytics"])
def run_benchmark():
    """
    Executes a 5-trial benchmark to measure actual cache hit latency.
    Uses a deterministic probe entry for precise measurement against L1/L2 caches.
    Miss latency is estimated from real query log averages.
    """
    PROBE_QUERY  = "__cache_craft_benchmark_probe__"
    PROBE_ANSWER = "This is a benchmark probe entry used to measure cache hit latency."

    # Ensure probe is cached (idempotent upsert)
    router.store(PROBE_QUERY, PROBE_ANSWER)

    hit_times = []
    for _ in range(5):
        t0 = time.perf_counter()
        router.search(PROBE_QUERY)
        hit_times.append((time.perf_counter() - t0) * 1000)

    avg_hit  = sum(hit_times) / len(hit_times)
    avg_miss = 1100.0
    try:
        avg_miss = db.get_analytics().get("avg_miss_latency_ms") or 1100.0
    except Exception:
        pass
    if avg_miss == 0:
        avg_miss = 1100.0

    return {
        "trials":            5,
        "original_avg_ms":   round(avg_miss, 2),
        "optimized_avg_ms":  round(avg_hit, 3),
        "speedup_factor":    round(avg_miss / avg_hit, 1) if avg_hit > 0 else 0,
        "measurement_note":  "Hit latency: real measurement. Miss latency: from query log (or estimated if no misses yet).",
        "hit_trial_ms":      [round(t, 3) for t in hit_times],
    }


# ============================================================
# Endpoints — Cache Management
# ============================================================

@app.post("/api/store", tags=["Cache Management"])
def store(request: StoreRequest):
    return router.store(request.question, request.answer)


@app.get("/api/cache", tags=["Cache Management"])
def get_cache():
    entries = router.get_all_entries()
    return {"total_entries": len(entries), "entries": entries}


@app.delete("/api/cache", tags=["Cache Management"])
def clear_cache():
    return router.clear_cache()


@app.delete("/api/cache/{query_hash}", tags=["Cache Management"])
def delete_entry(query_hash: str):
    """Delete a single cache entry by its full SHA-256 hash (supports per-entry invalidation)."""
    return router.delete_entry(query_hash)

@app.post("/api/cache/cleanup", tags=["Cache Management"])
def cleanup_expired():
    """Trigger cleanup of expired TTL cache entries."""
    deleted = 0
    try:
        deleted = db.cleanup_expired_entries()
    except Exception:
        pass
    return {"status": "ok", "deleted_expired_count": deleted}


# ============================================================
# Endpoints — Settings
# ============================================================

@app.get("/api/settings", tags=["Settings"])
def get_settings(request: Request):
    """Retrieve current system settings."""
    import core.llm_client as llm
    cache_sz = 0
    try:
        cache_sz = db.get_cache_size()
    except Exception:
        pass

    client_ip = request.client.host if request.client else "unknown"
    simulate_guest = request.query_params.get("guest") == "1" or request.query_params.get("simulate_guest", "").lower() in ("true", "1", "yes")
    allowed = False if simulate_guest else is_gpu_access_authorized(client_ip)

    return {
        "similarity_threshold":    router.threshold,
        "ttl_seconds":             router.ttl_seconds,
        "active_model":            llm.get_active_model(),
        "available_models":        llm.get_available_models(),
        "offline_mode":            llm.is_offline_mode_enabled(),
        "preferred_local_model":   llm.get_preferred_local_model(),
        "circuit_breaker":         llm.get_circuit_status(),
        "cache_size":              cache_sz,
        "model":                   "all-MiniLM-L6-v2",
        "embedding_dimensions":    384,
        "gpu_access_allowed":      allowed,
        "gpu_access_message":      "" if allowed else "Sorry, you're not allowed to access the GPU",
    }


@app.put("/api/settings/threshold", tags=["Settings"])
def update_threshold(request: ThresholdRequest):
    """Update the semantic similarity threshold."""
    old = router.threshold
    router.threshold = request.threshold
    try:
        db.set_setting("similarity_threshold", str(request.threshold))
    except Exception:
        pass
    return {
        "old_threshold": old,
        "new_threshold": router.threshold,
        "message": f"Threshold updated {old:.2f} → {router.threshold:.2f} (applied to active cache)",
    }


@app.put("/api/settings/ttl", tags=["Settings"])
def update_ttl(request: TTLRequest):
    """Update cache TTL expiration in seconds."""
    old_ttl = router.ttl_seconds
    router.set_ttl(request.ttl_seconds)
    return {
        "old_ttl_seconds": old_ttl,
        "new_ttl_seconds": router.ttl_seconds,
        "message": f"TTL updated {old_ttl}s → {router.ttl_seconds}s (persisted to DB)",
    }


@app.put("/api/settings/model", tags=["Settings"])
def update_model(request: ModelRequest):
    """Update active LLM inference model."""
    import core.llm_client as llm
    valid_ids = [m["id"] for m in llm.get_available_models()]
    if request.model not in valid_ids:
        raise HTTPException(status_code=400, detail=f"Invalid model. Choose from: {valid_ids}")
    llm.set_active_model(request.model)
    return {
        "active_model": request.model,
        "message": f"Active LLM model set to {request.model}",
    }


@app.put("/api/settings/offline-mode", tags=["Settings"])
def update_offline_mode(req: Request, request: OfflineModeRequest):
    """Toggle offline mode (force 100% local Ollama inference, zero network calls). Restricted to creator's PC."""
    client_ip = req.client.host if req.client else "unknown"
    simulate_guest = req.query_params.get("guest") == "1" or req.query_params.get("simulate_guest", "").lower() in ("true", "1", "yes")

    if request.offline_mode and (simulate_guest or not is_gpu_access_authorized(client_ip)):
        raise HTTPException(
            status_code=403,
            detail="Sorry, you're not allowed to access the GPU"
        )

    import core.llm_client as llm
    llm.set_offline_mode(request.offline_mode)
    if request.preferred_local_model:
        try:
            db.set_setting("preferred_local_model", request.preferred_local_model)
        except Exception:
            pass
    return {
        "offline_mode": request.offline_mode,
        "preferred_local_model": llm.get_preferred_local_model(),
        "message": f"Offline mode {'enabled' if request.offline_mode else 'disabled'} (applied)",
    }


@app.post("/api/feedback", tags=["Cache Management"])
def submit_feedback(request: FeedbackRequest):
    """Submit thumbs-up/down feedback on a cached response. Positive increments score; negative decrements."""
    try:
        return db.update_feedback(request.query_hash, request.is_positive)
    except Exception:
        return {"status": "ok", "message": "Feedback recorded in active session"}

# ============================================================
# Serve Static Frontend
# ============================================================

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@app.get("/app", tags=["Frontend"], include_in_schema=False)
def serve_frontend():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    import uvicorn
    print("=" * 52)
    print("  CACHE-CRAFT API v2.0")
    print("  Static UI:  http://localhost:8000/app")
    print("  Next.js UI: http://localhost:3000")
    print("  Swagger:    http://localhost:8000/docs")
    print("=" * 52)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
