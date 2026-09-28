"""
Cache-Craft API Server

A multi-tier semantic cache middleware designed to reduce LLM API costs.
Implements a routing architecture: L1 (Redis Exact Hash) -> L2 (PostgreSQL Vector Search) -> L3 (LLM API).
"""

import time
import os
import json
import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, field_validator

from core.cache_router import CacheRouter
import core.database as db

app = FastAPI(
    title="Cache-Craft API",
    description="Multi-tier semantic cache — reduces LLM API cost via L0 Memory → L1 Hash → L2 Vector → L3 LLM routing.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load persisted threshold and TTL from DB on startup (survives restarts)
_saved = db.get_setting("similarity_threshold")
_saved_ttl = db.get_setting("ttl_seconds")
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
                ]
            }
        }
    }


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


# ============================================================
# Endpoints — Health
# ============================================================

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "Cache-Craft API", "version": "2.0.0"}


@app.get("/api/health", tags=["Health"])
def detailed_health():
    """Real health check: database + embedding model + LLM connectivity."""
    import requests as req

    db_ok = False
    try:
        db.get_cache_size()
        db_ok = True
    except Exception:
        pass

    llm_ok = False
    llm_model = None
    try:
        r = req.get("http://localhost:11434/api/tags", timeout=2)
        if r.status_code == 200:
            llm_ok = True
            models = r.json().get("models", [])
            if models:
                llm_model = models[0].get("name")
    except Exception:
        pass

    return {
        "status": "ok" if (db_ok and llm_ok) else "degraded",
        "database": "ok" if db_ok else "error",
        "llm": "ok" if llm_ok else "unavailable",
        "llm_model": llm_model or "unknown",
        "embedding_model": "all-MiniLM-L6-v2",
    }


# ============================================================
# Endpoints — Query
# ============================================================

@app.post("/api/query", tags=["Query"])
def query(request: QueryRequest):
    """Main endpoint — 4-tier cache lookup with automatic write-back."""
    return router.search(request.question, messages=request.messages)


# ============================================================
# Endpoints — Analytics
# ============================================================

@app.get("/api/history", tags=["Analytics"])
def get_history(limit: int = 100):
    return {"history": db.get_query_history(limit)}


@app.get("/api/metrics", tags=["Analytics"])
def get_metrics():
    """Real-time cache statistics with tier breakdown, hourly trend, and latency percentiles."""
    metrics = router.get_metrics()
    metrics["tier_breakdown"]       = db.get_tier_breakdown()
    metrics["hourly_stats"]         = db.get_hourly_stats(24)
    metrics["latency_percentiles"]  = db.get_latency_percentiles()
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
    avg_miss = db.get_analytics().get("avg_miss_latency_ms") or 0
    if avg_miss == 0:
        # No real misses recorded yet — use a conservative estimate
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


@app.post("/api/cache/cleanup", tags=["Cache Management"])
def cleanup_expired():
    """Trigger cleanup of expired TTL cache entries."""
    deleted = db.cleanup_expired_entries()
    return {"status": "ok", "deleted_expired_count": deleted}


# ============================================================
# Endpoints — Settings
# ============================================================

@app.get("/api/settings", tags=["Settings"])
def get_settings():
    """Retrieve current system settings."""
    import core.llm_client as llm
    return {
        "similarity_threshold":  router.threshold,
        "ttl_seconds":           router.ttl_seconds,
        "active_model":          llm.get_active_model(),
        "available_models":      llm.AVAILABLE_MODELS,
        "cache_size":            db.get_cache_size(),
        "model":                 "all-MiniLM-L6-v2",
        "embedding_dimensions":  384,
    }


@app.put("/api/settings/threshold", tags=["Settings"])
def update_threshold(request: ThresholdRequest):
    """Update the semantic similarity threshold."""
    old = router.threshold
    router.threshold = request.threshold
    db.set_setting("similarity_threshold", str(request.threshold))
    return {
        "old_threshold": old,
        "new_threshold": router.threshold,
        "message": f"Threshold updated {old:.2f} → {router.threshold:.2f} (persisted to DB)",
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
    valid_ids = [m["id"] for m in llm.AVAILABLE_MODELS]
    if request.model not in valid_ids:
        raise HTTPException(status_code=400, detail=f"Invalid model. Choose from: {valid_ids}")
    llm.set_active_model(request.model)
    return {
        "active_model": request.model,
        "message": f"Active LLM model set to {request.model}",
    }


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
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
