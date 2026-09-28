import os
import hashlib
import psycopg
from pgvector.psycopg import register_vector
import json
import numpy as np

DB_URL = os.environ.get("DATABASE_URL", "postgresql://cachecraft:cachepassword@localhost:5433/cachecraft_db")

def _get_raw_conn():
    return psycopg.connect(DB_URL, row_factory=psycopg.rows.dict_row)

def _get_conn():
    conn = _get_raw_conn()
    try:
        register_vector(conn)
    except psycopg.ProgrammingError:
        pass # Will be registered after init_db creates the extension
    return conn

def init_db():
    # Step 1: Create the extension on a raw connection
    with _get_raw_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()
            
    # Step 2: Now that it exists, use the full connection to build tables
    with _get_conn() as conn:
        with conn.cursor() as cur:
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS semantic_cache (
                    id SERIAL PRIMARY KEY,
                    query_text TEXT NOT NULL,
                    response_text TEXT NOT NULL,
                    embedding vector(384) NOT NULL,
                    query_hash TEXT UNIQUE NOT NULL,
                    hit_count INTEGER DEFAULT 0,
                    source TEXT DEFAULT 'manual',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_hit_at TIMESTAMP
                );
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS query_log (
                    id SERIAL PRIMARY KEY,
                    query_text TEXT NOT NULL,
                    result_type TEXT NOT NULL,
                    similarity_score REAL,
                    latency_ms REAL,
                    matched_query TEXT,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS benchmark_runs (
                    id SERIAL PRIMARY KEY,
                    test_name TEXT NOT NULL,
                    total_queries INTEGER,
                    cache_hits INTEGER,
                    cache_misses INTEGER,
                    avg_hit_latency_ms REAL,
                    avg_miss_latency_ms REAL,
                    cost_savings_percent REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
            """)
            
            # HNSW index for cosine distance
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_embedding
                ON semantic_cache USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """)
            
            cur.execute("CREATE INDEX IF NOT EXISTS idx_cache_hash ON semantic_cache(query_hash);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_log_type ON query_log(result_type);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_log_time ON query_log(created_at);")
            cur.execute("ALTER TABLE semantic_cache ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP;")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires_at ON semantic_cache(expires_at);")
        conn.commit()
    print(f"[Database] Ready at {DB_URL}")

def get_setting(key: str) -> str | None:
    with _get_conn() as conn:
        with conn.cursor() as cur:
            row = cur.execute("SELECT value FROM settings WHERE key = %s", (key,)).fetchone()
            return row["value"] if row else None

def set_setting(key: str, value: str):
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO settings (key, value) VALUES (%s, %s) "
                "ON CONFLICT(key) DO UPDATE SET value = EXCLUDED.value",
                (key, value)
            )
        conn.commit()

def cleanup_expired_entries() -> int:
    """Purge expired cache rows from database."""
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM semantic_cache WHERE expires_at IS NOT NULL AND expires_at <= CURRENT_TIMESTAMP")
            deleted = cur.rowcount
        conn.commit()
    return deleted

def store_entry(query_text: str, response_text: str, embedding, source: str = "manual", ttl_seconds: int = None) -> dict:
    query_hash = hashlib.sha256(query_text.lower().strip().encode()).hexdigest()
    # Handle list or numpy array
    if isinstance(embedding, list):
        embedding = np.array(embedding)

    with _get_conn() as conn:
        with conn.cursor() as cur:
            if ttl_seconds and ttl_seconds > 0:
                cur.execute(
                    """INSERT INTO semantic_cache 
                       (query_text, response_text, embedding, query_hash, source, hit_count, expires_at)
                       VALUES (%s, %s, %s, %s, %s, 0, CURRENT_TIMESTAMP + (%s || ' seconds')::interval)
                       ON CONFLICT(query_hash) DO UPDATE SET
                           response_text = EXCLUDED.response_text,
                           embedding     = EXCLUDED.embedding,
                           source        = EXCLUDED.source,
                           expires_at    = EXCLUDED.expires_at""",
                    (query_text, response_text, embedding, query_hash, source, str(ttl_seconds))
                )
            else:
                cur.execute(
                    """INSERT INTO semantic_cache 
                       (query_text, response_text, embedding, query_hash, source, hit_count, expires_at)
                       VALUES (%s, %s, %s, %s, %s, 0, NULL)
                       ON CONFLICT(query_hash) DO UPDATE SET
                           response_text = EXCLUDED.response_text,
                           embedding     = EXCLUDED.embedding,
                           source        = EXCLUDED.source,
                           expires_at    = EXCLUDED.expires_at""",
                    (query_text, response_text, embedding, query_hash, source)
                )
        conn.commit()
    return {"status": "stored", "query_hash": query_hash}

def store_entries_batch(entries: list[dict], ttl_seconds: int = None) -> int:
    """Batch insert multiple Q&A entries in a single database transaction."""
    with _get_conn() as conn:
        with conn.cursor() as cur:
            for e in entries:
                q_text = e["query_text"]
                ans = e["response_text"]
                emb = np.array(e["embedding"]) if isinstance(e["embedding"], list) else e["embedding"]
                q_hash = hashlib.sha256(q_text.lower().strip().encode()).hexdigest()
                source = e.get("source", "manual")
                if ttl_seconds and ttl_seconds > 0:
                    cur.execute(
                        """INSERT INTO semantic_cache 
                           (query_text, response_text, embedding, query_hash, source, hit_count, expires_at)
                           VALUES (%s, %s, %s, %s, %s, 0, CURRENT_TIMESTAMP + (%s || ' seconds')::interval)
                           ON CONFLICT(query_hash) DO UPDATE SET
                               response_text = EXCLUDED.response_text,
                               embedding     = EXCLUDED.embedding,
                               source        = EXCLUDED.source,
                               expires_at    = EXCLUDED.expires_at""",
                        (q_text, ans, emb, q_hash, source, str(ttl_seconds))
                    )
                else:
                    cur.execute(
                        """INSERT INTO semantic_cache 
                           (query_text, response_text, embedding, query_hash, source, hit_count, expires_at)
                           VALUES (%s, %s, %s, %s, %s, 0, NULL)
                       ON CONFLICT(query_hash) DO UPDATE SET
                           response_text = EXCLUDED.response_text,
                           embedding     = EXCLUDED.embedding,
                           source        = EXCLUDED.source,
                           expires_at    = EXCLUDED.expires_at""",
                    (q_text, ans, emb, q_hash, source)
                )
        conn.commit()
    return len(entries)

def lookup_by_hash(query_hash: str) -> dict | None:
    with _get_conn() as conn:
        with conn.cursor() as cur:
            row = cur.execute(
                "SELECT * FROM semantic_cache WHERE query_hash = %s AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)",
                (query_hash,)
            ).fetchone()
            if row:
                cur.execute("UPDATE semantic_cache SET hit_count = hit_count + 1, last_hit_at = CURRENT_TIMESTAMP WHERE id = %s", (row["id"],))
                conn.commit()
                return dict(row)
    return None

def semantic_search(query_embedding, threshold: float, is_followup: bool = False):
    if isinstance(query_embedding, list):
        query_embedding = np.array(query_embedding)
        
    with _get_conn() as conn:
        with conn.cursor() as cur:
            # pgvector operator <=> is cosine distance. 
            # cosine similarity = 1 - cosine distance
            # So distance <= 1 - threshold
            max_distance = 1.0 - threshold
            filter_sql = "AND query_text LIKE '%% -> %%'" if is_followup else "AND query_text NOT LIKE '%% -> %%'"
            
            cur.execute(f"""
                SELECT id, query_text, response_text, query_hash, 
                       1 - (embedding <=> %s) AS similarity_score
                FROM semantic_cache
                WHERE embedding <=> %s <= %s AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP) {filter_sql}
                ORDER BY embedding <=> %s
                LIMIT 1
            """, (query_embedding, query_embedding, max_distance, query_embedding))
            
            row = cur.fetchone()
            if row:
                cur.execute("UPDATE semantic_cache SET hit_count = hit_count + 1, last_hit_at = CURRENT_TIMESTAMP WHERE id = %s", (row["id"],))
                conn.commit()
                return dict(row)
    return None

def get_all_entries() -> list:
    with _get_conn() as conn:
        with conn.cursor() as cur:
            rows = cur.execute(
                """SELECT id, query_text, response_text, query_hash, hit_count,
                          source, created_at, last_hit_at
                   FROM semantic_cache ORDER BY created_at DESC"""
            ).fetchall()
    return [dict(r) for r in rows]

def clear_all():
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE semantic_cache RESTART IDENTITY CASCADE;")
        conn.commit()
    return {"status": "cleared"}

def log_query(query_text: str, result_type: str, similarity_score: float = None, latency_ms: float = None, matched_query: str = None, source: str = None):
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO query_log 
                   (query_text, result_type, similarity_score, latency_ms, matched_query, source)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (query_text, result_type, similarity_score, latency_ms, matched_query, source)
            )
        conn.commit()

def get_analytics() -> dict:
    with _get_conn() as conn:
        with conn.cursor() as cur:
            agg = cur.execute("""
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN result_type = 'CACHE_HIT' THEN 1 ELSE 0 END) AS hits,
                    SUM(CASE WHEN result_type = 'CACHE_MISS' THEN 1 ELSE 0 END) AS misses,
                    AVG(CASE WHEN result_type = 'CACHE_HIT' THEN latency_ms END) AS avg_hit_lat,
                    AVG(CASE WHEN result_type = 'CACHE_MISS' THEN latency_ms END) AS avg_miss_lat
                FROM query_log
            """).fetchone()
            cache_count = cur.execute("SELECT COUNT(*) FROM semantic_cache").fetchone()["count"]

    total = agg["total"] or 0
    hits = agg["hits"] or 0
    misses = agg["misses"] or 0
    hit_rate = (hits / total * 100) if total > 0 else 0

    return {
        "total_queries": total,
        "cache_hits": hits,
        "cache_misses": misses,
        "hit_rate_percent": round(hit_rate, 2),
        "avg_hit_latency_ms": round(agg["avg_hit_lat"] or 0, 2),
        "avg_miss_latency_ms": round(agg["avg_miss_lat"] or 0, 2),
        "cost_savings_percent": round(hit_rate, 2),
        "cache_size": cache_count,
    }

def get_cache_size() -> int:
    with _get_conn() as conn:
        with conn.cursor() as cur:
            return cur.execute("SELECT COUNT(*) FROM semantic_cache").fetchone()["count"]

def get_query_history(limit: int = 100) -> list:
    with _get_conn() as conn:
        with conn.cursor() as cur:
            rows = cur.execute(
                """SELECT id, query_text, result_type, similarity_score, 
                          latency_ms, matched_query, source, created_at
                   FROM query_log 
                   ORDER BY created_at DESC 
                   LIMIT %s""", 
                (limit,)
            ).fetchall()
    return [dict(r) for r in rows]

def get_tier_breakdown() -> dict:
    with _get_conn() as conn:
        with conn.cursor() as cur:
            rows = cur.execute("SELECT source, COUNT(*) as count FROM query_log GROUP BY source").fetchall()
            # source could be 'L1 (Redis)', 'L2 (pgvector)', 'LLM API' etc.
            return {r["source"] or "Unknown": r["count"] for r in rows}

def get_hourly_stats(hours: int = 24) -> list:
    with _get_conn() as conn:
        with conn.cursor() as cur:
            rows = cur.execute(
                """SELECT DATE_TRUNC('hour', created_at) as hour, 
                          SUM(CASE WHEN result_type = 'CACHE_HIT' THEN 1 ELSE 0 END) as hits,
                          SUM(CASE WHEN result_type = 'CACHE_MISS' THEN 1 ELSE 0 END) as misses
                   FROM query_log 
                   WHERE created_at >= NOW() - INTERVAL '%s hours'
                   GROUP BY hour ORDER BY hour ASC""", 
                (hours,)
            ).fetchall()
            return [{"time": r["hour"].isoformat(), "hits": r["hits"] or 0, "misses": r["misses"] or 0} for r in rows]

def get_latency_percentiles() -> dict:
    with _get_conn() as conn:
        with conn.cursor() as cur:
            # Check if there are any rows first to avoid error on empty percentiles
            count = cur.execute("SELECT COUNT(*) FROM query_log").fetchone()["count"]
            if count == 0:
                return {"p50": 0, "p90": 0, "p99": 0}
            
            row = cur.execute(
                """SELECT 
                      percentile_cont(0.5) WITHIN GROUP (ORDER BY latency_ms) as p50,
                      percentile_cont(0.9) WITHIN GROUP (ORDER BY latency_ms) as p90,
                      percentile_cont(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99
                   FROM query_log"""
            ).fetchone()
            return {
                "p50": round(row["p50"] or 0, 2),
                "p90": round(row["p90"] or 0, 2),
                "p99": round(row["p99"] or 0, 2)
            }

init_db()
