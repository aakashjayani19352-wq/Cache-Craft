import hashlib
import time
import os
import json
import redis
from core.embedder import Embedder
import core.database as db
from core.llm_client import generate_answer

# Redis L1 Cache Connection
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

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


class CacheRouter:
    """
    The central intelligence of Cache-Craft.
    3-Tier lookup: Redis (Hash) → PostgreSQL+pgvector (Semantic) → LLM
    """

    def __init__(self, similarity_threshold: float = 0.85, ttl_seconds: int = 86400):
        self.embedder = Embedder()
        self.threshold = similarity_threshold
        self.ttl_seconds = ttl_seconds

    def _hash_query(self, query: str) -> str:
        """Create a SHA-256 fingerprint of the query text."""
        normalized = query.strip().lower()
        return hashlib.sha256(normalized.encode()).hexdigest()

    def search(self, query: str, messages: list = None) -> dict:
        """
        The main entry point. 3-tier cache lookup with conversational context support.
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

        # --- Tier 1: Redis Exact Hash Match (O(1)) ---
        redis_hit = redis_client.get(query_hash)
        if redis_hit:
            redis_data = json.loads(redis_hit)
            elapsed_ms = (time.time() - start_time) * 1000
            
            db.log_query(query, "CACHE_HIT", 1.0, elapsed_ms, redis_data["query_text"], "L1 (Redis)")
            db.lookup_by_hash(query_hash)
            
            return {
                "status": "CACHE_HIT",
                "match_type": "EXACT",
                "similarity_score": 1.0,
                "original_query": redis_data["query_text"],
                "response": redis_data["response_text"],
                "latency_ms": round(elapsed_ms, 2),
                "source": "L1 (Redis Cache)"
            }

        # --- Tier 2: Semantic Vector Search (PostgreSQL + pgvector) ---
        query_embedding = self.embedder.encode(lookup_query)
        best_match = db.semantic_search(query_embedding, self.threshold, is_followup=is_followup)

        if best_match:
            elapsed_ms = (time.time() - start_time) * 1000
            
            cache_payload = {
                "query_text": best_match["query_text"],
                "response_text": best_match["response_text"]
            }
            redis_client.set(query_hash, json.dumps(cache_payload), ex=86400)
            
            db.log_query(query, "CACHE_HIT", float(best_match["similarity_score"]), elapsed_ms, best_match["query_text"], "L2 (pgvector)")
            return {
                "status": "CACHE_HIT",
                "match_type": "SEMANTIC",
                "similarity_score": round(float(best_match["similarity_score"]), 4),
                "original_query": best_match["query_text"],
                "response": best_match["response_text"],
                "latency_ms": round(elapsed_ms, 2),
                "source": "L2 (PostgreSQL pgvector)"
            }

        # --- Tier 3: Cache Miss → Call Ollama LLM with multi-turn history ---
        llm_response = generate_answer(query, messages=messages)
        
        if llm_response["error"] is None:
            # Store in PostgreSQL L2
            db.store_entry(lookup_query, llm_response["answer"], query_embedding, source="local_llm", ttl_seconds=self.ttl_seconds)
            # Store in Redis L1
            cache_payload = {
                "query_text": lookup_query,
                "response_text": llm_response["answer"]
            }
            redis_kwargs = {"ex": self.ttl_seconds} if self.ttl_seconds and self.ttl_seconds > 0 else {}
            redis_client.set(query_hash, json.dumps(cache_payload), **redis_kwargs)
            
        elapsed_ms = (time.time() - start_time) * 1000
        db.log_query(query, "CACHE_MISS", 0.0, elapsed_ms, None, "LLM API")
        
        return {
            "status": "CACHE_MISS",
            "match_type": None,
            "similarity_score": 0.0,
            "closest_query": None,
            "response": llm_response["answer"],
            "latency_ms": round(elapsed_ms, 2),
            "source": f"LLM API ({llm_response['model']})"
        }

    def store(self, query: str, response: str) -> dict:
        """Manually store a question-answer pair."""
        embedding = self.embedder.encode(query)
        query_hash = self._hash_query(query)
        
        cache_payload = {
            "query_text": query,
            "response_text": response
        }
        redis_kwargs = {"ex": self.ttl_seconds} if self.ttl_seconds and self.ttl_seconds > 0 else {}
        redis_client.set(query_hash, json.dumps(cache_payload), **redis_kwargs)
        return db.store_entry(query, response, embedding, ttl_seconds=self.ttl_seconds)

    def set_ttl(self, ttl_seconds: int) -> int:
        """Update and persist TTL duration."""
        self.ttl_seconds = ttl_seconds
        db.set_setting("ttl_seconds", str(ttl_seconds))
        return self.ttl_seconds

    def get_metrics(self) -> dict:
        """Return analytics from the database."""
        metrics = db.get_analytics()
        metrics["similarity_threshold"] = self.threshold
        return metrics

    def get_all_entries(self) -> list[dict]:
        """Return all cached entries."""
        entries = db.get_all_entries()
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
        redis_client.flushdb()
        return db.clear_all()
