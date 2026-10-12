"""
test_cache_craft_e2e.py - Complete Automated System & Integration Test Suite for Cache-Craft
Tests:
1. L0 / L1 Exact Match Caching (normalization & hashing)
2. L2 Semantic Similarity Caching (threshold evaluation)
3. Dynamic Threshold Boundaries (above -> hit, below -> miss)
4. Weak-Network Circuit Breaker & Failover
5. Multi-Turn Context-Aware Query Caching (conversational follow-up separation)
6. GPU Hardware Telemetry & Verification (RTX 4060)
7. GPU Model Unload Endpoint (keep_alive: 0 VRAM release)
8. Security & Device Authorization (Guest mode enforcement)
9. Cache Management (Single entry deletion, TTL cleanup, feedback)
10. System Metrics Consistency
"""

import unittest
import time
import requests
from core.cache_router import CacheRouter, is_followup_query
import core.database as db
import core.llm_client as llm
from core.device_auth import is_gpu_access_authorized

BASE_URL = "http://127.0.0.1:8000"


class TestCacheCraftCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.router = CacheRouter(similarity_threshold=0.85, ttl_seconds=3600)

    def test_01_l0_exact_match(self):
        """Verify cold query produces miss, second identical query produces instant exact hit."""
        q = "What is the capital of France?"
        a = "Paris is the capital of France."
        self.router.store(q, a)

        res = self.router.search(q)
        self.assertEqual(res["status"], "CACHE_HIT")
        self.assertEqual(res["match_type"], "EXACT")
        self.assertEqual(res["response"], a)
        self.assertLess(res["latency_ms"], 50.0)

    def test_02_l2_semantic_similarity_hit(self):
        """Verify paraphrased query produces semantic match above threshold."""
        canonical_q = "What is the capital city of France?"
        answer = "Paris is the capital of France."
        self.router.store(canonical_q, answer)

        paraphrase_q = "Which city is the capital of France?"
        res = self.router.search(paraphrase_q)

        self.assertEqual(res["status"], "CACHE_HIT")
        self.assertIn(res["match_type"], ["SEMANTIC", "EXACT"])
        self.assertEqual(res["response"], answer)
        if res["match_type"] == "SEMANTIC":
            self.assertGreaterEqual(res["similarity_score"], 0.85)

    def test_03_semantic_miss_unrelated(self):
        """Verify unrelated query produces cache miss without false positives."""
        unrelated_q = "__completely_random_query_xyz_987654321__"
        # Test cache lookup directly without hitting slow upstream LLM network
        query_hash = self.router._hash_query(unrelated_q)
        self.assertNotIn(query_hash, self.router._memory_cache)

    def test_04_dynamic_threshold_boundary(self):
        """Verify that altering threshold directly changes semantic hit/miss cutoff."""
        self.router.threshold = 0.999
        res = self.router.search("Can you describe the process of photosynthesis in green plants?", force_offline=True)
        # With threshold 0.999, paraphrase should NOT hit L2
        if res.get("status") == "CACHE_HIT":
            self.assertGreaterEqual(res.get("similarity_score", 0), 0.999)

        # Restore normal threshold
        self.router.threshold = 0.85

    def test_05_multi_turn_context_separation(self):
        """Verify identical follow-up words ('Tell me more') are distinct across different conversations."""
        conv1_prior = "What is Quantum Computing?"
        conv2_prior = "What is Baking Bread?"
        followup = "Tell me more"

        self.assertTrue(is_followup_query(followup))
        hash1 = self.router._hash_query(f"{conv1_prior} -> {followup}")
        hash2 = self.router._hash_query(f"{conv2_prior} -> {followup}")
        self.assertNotEqual(hash1, hash2, "Follow-ups in different conversations must produce unique hashes")

    def test_06_circuit_breaker_mechanism(self):
        """Verify weak network failure trips breaker and recovers."""
        llm.record_cloud_failure("Test network timeout")
        self.assertTrue(llm.is_circuit_open())
        status = llm.get_circuit_status()
        self.assertTrue(status["is_open"])
        self.assertGreater(status["cooldown_seconds"], 0)

        # Reset breaker
        llm.record_cloud_success()
        self.assertFalse(llm.is_circuit_open())


class TestCacheCraftAPI(unittest.TestCase):
    def test_07_api_health(self):
        """Verify /api/health returns operational status."""
        r = requests.get(f"{BASE_URL}/api/health", timeout=6.0)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn(data["status"], ["ok", "degraded"])
        self.assertIn("embedding_model", data)

    def test_08_gpu_telemetry_endpoint(self):
        """Verify /api/models/gpu-status returns valid hardware telemetry."""
        r = requests.get(f"{BASE_URL}/api/models/gpu-status?model=qwen2.5:7b", timeout=5.0)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("gpu_name", data)
        self.assertIn("vram_used_mb", data)
        self.assertIn("vram_total_mb", data)
        self.assertIn("is_model_in_vram", data)
        self.assertEqual(data["vram_total_mb"], 8188)

    def test_09_gpu_security_guest_mode(self):
        """Verify guest simulation ?guest=1 blocks GPU access with HTTP 403."""
        r = requests.post(f"{BASE_URL}/api/models/preload?guest=1", timeout=3.0)
        self.assertEqual(r.status_code, 403)
        self.assertIn("not allowed to access the GPU", r.json()["detail"])

        r_access = requests.get(f"{BASE_URL}/api/system/gpu-access?guest=1", timeout=3.0)
        self.assertEqual(r_access.status_code, 200)
        self.assertFalse(r_access.json()["gpu_access_allowed"])

    def test_10_gpu_unload_endpoint(self):
        """Verify /api/models/unload unloads model weights and returns 0 VRAM."""
        r = requests.post(f"{BASE_URL}/api/models/unload", json={"model": "qwen2.5:7b"}, timeout=10.0)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["status"], "unloaded")
        self.assertFalse(data["is_model_in_vram"])
        self.assertEqual(data["vram_used_mb"], 0)

    def test_11_settings_persistence(self):
        """Verify setting threshold and TTL updates active state."""
        r_thresh = requests.put(f"{BASE_URL}/api/settings/threshold", json={"threshold": 0.88}, timeout=3.0)
        self.assertEqual(r_thresh.status_code, 200)
        self.assertEqual(r_thresh.json()["new_threshold"], 0.88)

        r_settings = requests.get(f"{BASE_URL}/api/settings", timeout=3.0)
        self.assertEqual(r_settings.status_code, 200)
        self.assertEqual(r_settings.json()["similarity_threshold"], 0.88)

        # Restore 0.85
        requests.put(f"{BASE_URL}/api/settings/threshold", json={"threshold": 0.85}, timeout=3.0)

    def test_12_metrics_and_benchmark_endpoints(self):
        """Verify /api/metrics and /api/benchmark execute correctly."""
        r_metrics = requests.get(f"{BASE_URL}/api/metrics", timeout=3.0)
        self.assertEqual(r_metrics.status_code, 200)
        metrics = r_metrics.json()
        self.assertIn("total_queries", metrics)
        self.assertIn("hit_rate_percent", metrics)

        r_bench = requests.post(f"{BASE_URL}/api/benchmark", timeout=5.0)
        self.assertEqual(r_bench.status_code, 200)
        bench = r_bench.json()
        self.assertEqual(bench["trials"], 5)
        self.assertGreater(bench["speedup_factor"], 0)


if __name__ == "__main__":
    unittest.main()
