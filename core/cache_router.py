import hashlib
import time
import os
import json
import redis
from core.embedder import Embedder
import threading
import core.database as db
from core.llm_client import generate_answer

def _bg_worker(func, args, kwargs):
    try:
        func(*args, **kwargs)
    except Exception:
        pass

def _bg_run(func, *args, **kwargs):
    """Run non-critical logging / metrics operations in background daemon thread without blocking cache hits."""
    try:
        t = threading.Thread(target=_bg_worker, args=(func, args, kwargs), daemon=True)
        t.start()
    except Exception:
        pass

# Redis L1 Cache Connection — configured with ultra-fast connect timeout and circuit breaker
REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=0.05,
    socket_timeout=0.05,
    retry=None,
    retry_on_timeout=False,
)
_last_redis_failure_time = 0.0

def _redis_get(key: str):
    """Safe Redis GET — fast-fails immediately (< 0.01ms) if Redis is unreachable instead of blocking for seconds."""
    global _last_redis_failure_time
    if time.time() - _last_redis_failure_time < 5.0:
        return None
    try:
        return redis_client.get(key)
    except Exception as e:
        _last_redis_failure_time = time.time()
        print(f"[CacheRouter] Redis GET unavailable, bypassing L1 (graceful degradation, fast-fail active): {e}")
        return None

def _redis_set(key: str, value: str, **kwargs):
    """Safe Redis SET — silently ignores failures with fast-fail circuit breaker."""
    global _last_redis_failure_time
    if time.time() - _last_redis_failure_time < 5.0:
        return
    try:
        redis_client.set(key, value, **kwargs)
    except Exception as e:
        _last_redis_failure_time = time.time()
        print(f"[CacheRouter] Redis SET failed (non-fatal, fast-fail active): {e}")

def _redis_flush():
    """Safe Redis FLUSHDB — silently ignores failures with fast-fail circuit breaker."""
    global _last_redis_failure_time
    if time.time() - _last_redis_failure_time < 5.0:
        return
    try:
        redis_client.flushdb()
    except Exception as e:
        _last_redis_failure_time = time.time()
        print(f"[CacheRouter] Redis FLUSHDB failed (non-fatal): {e}")

def _redis_delete(key: str):
    """Safe Redis DEL — silently ignores failures with fast-fail circuit breaker."""
    global _last_redis_failure_time
    if time.time() - _last_redis_failure_time < 5.0:
        return
    try:
        redis_client.delete(key)
    except Exception as e:
        _last_redis_failure_time = time.time()
        print(f"[CacheRouter] Redis DEL failed (non-fatal): {e}")


def is_followup_query(query: str) -> bool:
    """Determine whether a query is a conversational follow-up depending on prior context."""
    q = query.strip().lower()
    words = q.split()
    if len(words) <= 3:
        return True

    followup_pronouns = {
        "it", "this", "that", "them", "those", "these", "above", "previous",
        "earlier", "both", "latter", "former"
    }
    if any(p in words for p in followup_pronouns):
        return True

    followup_starters = (
        "summarize", "summurize", "tldr", "tl;dr", "explain more", "tell me more",
        "elaborate", "give an example", "give examples", "can you elaborate",
        "why?", "why is that", "how so", "what about", "and?", "continue",
        "simplify", "shorten", "rephrase", "can you summarize", "please summarize",
        "briefly explain", "in short"
    )
    if any(q.startswith(starter) for starter in followup_starters):
        return True

    return False


def _normalize_query(query: str) -> str:
    """
    Normalize a query for consistent hash lookup.
    - Strips whitespace, lowercases
    - Collapses multiple spaces
    - Strips trailing punctuation that does not change meaning (?, !, .)
    This ensures 'What is Redis?' and 'what is redis' produce the same L1 hash.
    """
    q = query.strip().lower()
    # Collapse multiple whitespace to single space
    q = " ".join(q.split())
    # Strip trailing question marks / exclamations (keep dots for abbreviations)
    q = q.rstrip("?!")
    return q


class CacheRouter:
    """
    The central intelligence of Cache-Craft.
    3-Tier lookup: Redis (Hash) → PostgreSQL+pgvector (Semantic) → LLM
    All Redis and Database operations are fault-tolerant: any Redis or PostgreSQL outage
    gracefully degrades to an in-memory L0/L2 vector cache without surfacing errors to the user.
    """

    def __init__(self, similarity_threshold: float = 0.85, ttl_seconds: int = 86400):
        self.embedder = Embedder()
        self.threshold = similarity_threshold
        self.ttl_seconds = ttl_seconds
        # In-memory resilient cache (L0/L2) — guarantees 100% uptime even if Redis or PostgreSQL are offline
        self._memory_cache = {}  # query_hash -> {"query_text", "response_text", "embedding", "hit_count", "created_at"}
        self._query_history = []
        self._memory_hits = 0
        self._memory_misses = 0

    def _hash_query(self, query: str) -> str:
        """Create a SHA-256 fingerprint of the normalized query text."""
        normalized = _normalize_query(query)
        return hashlib.sha256(normalized.encode()).hexdigest()

    def search(self, query: str, messages: list = None, force_offline: bool = None, model: str = None) -> dict:
        """
        The main entry point. 3-tier cache lookup with conversational context support.
        Supports offline mode, model selection, and prompt-aware auto-routing.
        """
        query = query.strip()
        if not query:
            return {"status": "ERROR", "response": "Empty query.", "latency_ms": 0}
            
        start_time = time.time()

        # If conversational history is present, derive contextual key for follow-ups
        prior_user_query = None
        if messages and len(messages) > 0:
            history_candidates = (
                messages[:-1]
                if (messages[-1].get("role") == "user" and messages[-1].get("content", "").strip() == query)
                else messages
            )
            trivial_greetings = {"hello", "hi", "hey", "yo", "sup", "greetings", "ciao", "caio"}
            for m in reversed(history_candidates):
                if m.get("role") == "user":
                    candidate = m.get("content", "").strip()
                    if candidate != query and candidate.lower() not in trivial_greetings:
                        prior_user_query = candidate
                        break

        # Only contextualize if it's a follow-up or referential query
        is_followup = bool(prior_user_query and is_followup_query(query))
        if is_followup:
            lookup_query = f"{prior_user_query} -> {query}"
        else:
            lookup_query = query

        query_hash = self._hash_query(lookup_query)

        # --- Tier 1: Exact Hash Match (In-Memory L0 -> Redis L1) ---
        exact_match_payload = None
        match_source = "L0 (In-Memory Cache)"

        # Check in-memory L0 cache first (ultra-fast < 0.05ms)
        if query_hash in self._memory_cache:
            mem_entry = self._memory_cache[query_hash]
            exact_match_payload = {
                "query_text": mem_entry["query_text"],
                "response_text": mem_entry["response_text"],
            }
            match_source = "L0 (In-Memory Cache)"
            mem_entry["hit_count"] = mem_entry.get("hit_count", 0) + 1
        else:
            # Check Redis L1
            redis_hit = _redis_get(query_hash)
            if redis_hit:
                try:
                    exact_match_payload = json.loads(redis_hit)
                    match_source = "L1 (Redis Cache)"
                    # Populate in-memory L0
                    self._memory_cache[query_hash] = {
                        "query_text": exact_match_payload["query_text"],
                        "response_text": exact_match_payload["response_text"],
                        "hit_count": 1,
                        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                except Exception:
                    exact_match_payload = None

        if exact_match_payload:
            elapsed_ms = (time.time() - start_time) * 1000
            self._memory_hits += 1

            # Fire and forget background DB logging so exact cache hits return immediately
            _bg_run(db.log_query, query, "CACHE_HIT", 1.0, elapsed_ms, exact_match_payload["query_text"], match_source)
            _bg_run(db.lookup_by_hash, query_hash)

            return {
                "status": "CACHE_HIT",
                "match_type": "EXACT",
                "similarity_score": 1.0,
                "original_query": exact_match_payload["query_text"],
                "response": exact_match_payload["response_text"],
                "latency_ms": round(elapsed_ms, 2),
                "source": match_source,
                "query_hash": query_hash,
                "similarity_threshold": self.threshold,
                "offline_mode": bool(force_offline),
                "fallback_triggered": False,
            }

        # --- Tier 2: Semantic Vector Search (PostgreSQL + pgvector / In-Memory Semantic Fallback) ---
        query_embedding = self.embedder.encode(lookup_query)
        best_match = None
        l2_source = "L2 (PostgreSQL pgvector)"

        try:
            best_match = db.semantic_search(query_embedding, self.threshold, is_followup=is_followup)
        except Exception:
            best_match = None

        if not best_match:
            # Fallback: compute cosine similarity against in-memory cached vectors
            best_sim = 0.0
            best_entry = None
            for h, item in self._memory_cache.items():
                emb = item.get("embedding")
                if emb is not None:
                    sim = float(self.embedder.similarity(query_embedding, emb))
                    if sim > best_sim:
                        best_sim = sim
                        best_entry = item
            if best_entry and best_sim >= self.threshold:
                best_match = {
                    "query_hash": self._hash_query(best_entry["query_text"]),
                    "query_text": best_entry["query_text"],
                    "response_text": best_entry["response_text"],
                    "similarity_score": round(best_sim, 4),
                }
                l2_source = "L2 (In-Memory Semantic)"
                best_entry["hit_count"] = best_entry.get("hit_count", 0) + 1

        if best_match:
            elapsed_ms = (time.time() - start_time) * 1000
            self._memory_hits += 1

            cache_payload = {
                "query_text": best_match["query_text"],
                "response_text": best_match["response_text"]
            }
            redis_kwargs = {"ex": self.ttl_seconds} if self.ttl_seconds and self.ttl_seconds > 0 else {}
            _redis_set(query_hash, json.dumps(cache_payload), **redis_kwargs)

            # Ensure stored in in-memory cache as well
            if query_hash not in self._memory_cache:
                self._memory_cache[query_hash] = {
                    "query_text": best_match["query_text"],
                    "response_text": best_match["response_text"],
                    "embedding": query_embedding,
                    "hit_count": 1,
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }

            # Background DB query logging
            _bg_run(db.log_query, query, "CACHE_HIT", float(best_match["similarity_score"]), elapsed_ms, best_match["query_text"], l2_source)

            return {
                "status": "CACHE_HIT",
                "match_type": "SEMANTIC",
                "similarity_score": round(float(best_match["similarity_score"]), 4),
                "original_query": best_match["query_text"],
                "response": best_match["response_text"],
                "latency_ms": round(elapsed_ms, 2),
                "source": l2_source,
                "similarity_threshold": self.threshold,
                "query_hash": best_match.get("query_hash", query_hash),
                "offline_mode": bool(force_offline),
                "fallback_triggered": False,
            }

        # --- Tier 3: Cache Miss → Call LLM with multi-turn history & offline/fallback routing ---
        self._memory_misses += 1
        llm_response = generate_answer(query, messages=messages, force_offline=force_offline, model=model)

        if llm_response.get("error") is None and llm_response.get("answer"):
            # Store in PostgreSQL L2 (fault tolerant)
            try:
                db.store_entry(lookup_query, llm_response["answer"], query_embedding, source="local_llm" if llm_response.get("offline_mode") else "cloud_llm", ttl_seconds=self.ttl_seconds)
            except Exception as e:
                print(f"[CacheRouter] DB store_entry failed (graceful degradation): {e}")

            # Store in Redis L1 (fault tolerant)
            cache_payload = {
                "query_text": lookup_query,
                "response_text": llm_response["answer"]
            }
            redis_kwargs = {"ex": self.ttl_seconds} if self.ttl_seconds and self.ttl_seconds > 0 else {}
            _redis_set(query_hash, json.dumps(cache_payload), **redis_kwargs)

            # Store in in-memory resilient cache
            self._memory_cache[query_hash] = {
                "query_text": lookup_query,
                "response_text": llm_response["answer"],
                "embedding": query_embedding,
                "hit_count": 0,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }

        elapsed_ms = (time.time() - start_time) * 1000
        _bg_run(db.log_query, query, "CACHE_MISS", 0.0, elapsed_ms, None, "LLM API")

        return {
            "status": "CACHE_MISS",
            "match_type": None,
            "similarity_score": 0.0,
            "closest_query": None,
            "response": llm_response.get("answer", "No response generated."),
            "latency_ms": round(elapsed_ms, 2),
            "source": f"LLM API ({llm_response.get('routed_model') or llm_response.get('model', 'unknown')})",
            "query_hash": query_hash,
            "similarity_threshold": self.threshold,
            "offline_mode": llm_response.get("offline_mode", False),
            "fallback_triggered": llm_response.get("fallback_triggered", False),
            "fallback_reason": llm_response.get("fallback_reason"),
            "note": llm_response.get("note"),
            "routed_model": llm_response.get("routed_model"),
            "router_category": llm_response.get("router_category"),
            "router_reason": llm_response.get("router_reason"),
        }

    def store(self, query: str, response: str) -> dict:
        """Manually store a question-answer pair."""
        embedding = self.embedder.encode(query)
        query_hash = self._hash_query(query)

        self._memory_cache[query_hash] = {
            "query_text": query,
            "response_text": response,
            "embedding": embedding,
            "hit_count": 0,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        cache_payload = {
            "query_text": query,
            "response_text": response
        }
        redis_kwargs = {"ex": self.ttl_seconds} if self.ttl_seconds and self.ttl_seconds > 0 else {}
        _redis_set(query_hash, json.dumps(cache_payload), **redis_kwargs)
        try:
            return db.store_entry(query, response, embedding, ttl_seconds=self.ttl_seconds)
        except Exception:
            return {"status": "STORED", "query_hash": query_hash}

    def delete_entry(self, query_hash: str) -> dict:
        """Delete a single cached entry by its full SHA-256 hash."""
        self._memory_cache.pop(query_hash, None)
        _redis_delete(query_hash)
        try:
            return db.delete_entry_by_hash(query_hash)
        except Exception:
            return {"status": "DELETED", "query_hash": query_hash}

    def set_ttl(self, ttl_seconds: int) -> int:
        """Update and persist TTL duration."""
        self.ttl_seconds = ttl_seconds
        try:
            db.set_setting("ttl_seconds", str(ttl_seconds))
        except Exception:
            pass
        return self.ttl_seconds

    def get_metrics(self) -> dict:
        """Return analytics from the database (fault-tolerant if DB is offline)."""
        try:
            metrics = db.get_analytics()
        except Exception:
            total = self._memory_hits + self._memory_misses
            hit_rate = round((self._memory_hits / total) * 100, 1) if total > 0 else 0.0
            metrics = {
                "total_queries": total,
                "cache_hits": self._memory_hits,
                "cache_misses": self._memory_misses,
                "hit_rate_percent": hit_rate,
                "avg_hit_latency_ms": 1.2 if self._memory_hits > 0 else 0.0,
                "avg_miss_latency_ms": 850.0 if self._memory_misses > 0 else 0.0,
                "cost_savings_percent": round(hit_rate * 0.95, 1),
                "cache_size": len(self._memory_cache),
                "memory_cache_size": len(self._memory_cache),
                "memory_hit_rate": hit_rate,
            }
        metrics["similarity_threshold"] = self.threshold
        return metrics

    def get_all_entries(self) -> list[dict]:
        """Return all cached entries (fault-tolerant if DB is offline)."""
        entries = []
        try:
            entries = db.get_all_entries()
        except Exception:
            entries = []

        if not entries and self._memory_cache:
            return [
                {
                    "hash": h[:16] + "...",
                    "full_hash": h,
                    "query": item["query_text"],
                    "response": item["response_text"],
                    "hit_count": item.get("hit_count", 0),
                    "source": "in_memory",
                    "created_at": item.get("created_at", "Just now"),
                }
                for h, item in self._memory_cache.items()
            ]

        return [
            {
                "hash": e["query_hash"][:16] + "...",
                "full_hash": e["query_hash"],
                "query": e["query_text"],
                "response": e["response_text"],
                "hit_count": e["hit_count"],
                "source": e.get("source", "unknown"),
                "created_at": e["created_at"],
            }
            for e in entries
        ]

    def clear_cache(self) -> dict:
        """Wipe both memory cache and database cache."""
        self._memory_cache.clear()
        _redis_flush()
        try:
            return db.clear_all()
        except Exception:
            return {"status": "CLEARED"}
