/**
 * api.ts — Cache-Craft Backend API Client
 * All calls to http://localhost:8000
 */

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    cache: 'no-store',
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers }
  });
  if (!res.ok) throw new Error(`API ${path} → ${res.status}`);
  return res.json() as Promise<T>;
}

// ── Types ────────────────────────────────────────────────────────────────────

export interface TierBreakdown {
  [tier: string]: { count: number; avg_latency_ms: number };
}

export interface Metrics {
  total_queries: number;
  cache_hits: number;
  cache_misses: number;
  hit_rate_percent: number;
  avg_hit_latency_ms: number;
  avg_miss_latency_ms: number;
  cost_savings_percent: number;
  cache_size: number;
  similarity_threshold: number;
  memory_cache_size: number;
  memory_hit_rate: number;
  tier_breakdown: TierBreakdown;
  hourly_stats: { hour: string; total: number; hits: number }[];
  latency_percentiles: {
    hit: { p50: number; p90: number; p99: number };
    miss: { p50: number; p90: number; p99: number };
  };
}

export interface CacheEntry {
  hash: string;
  full_hash: string;
  query: string;
  response: string;
  hit_count: number;
  feedback_score: number;
  source: string;
  created_at: string;
}

export interface HistoryEntry {
  query_text: string;
  result_type: string;
  similarity_score: number;
  latency_ms: number;
  matched_query: string | null;
  source: string;
  created_at: string;
}

export interface ModelOption {
  id: string;
  name: string;
  provider: string;
  type: string;
  description: string;
}

export interface Settings {
  similarity_threshold: number;
  ttl_seconds?: number;
  active_model?: string;
  available_models?: ModelOption[];
  cache_size: number;
  model: string;
  embedding_dimensions: number;
}

export interface QueryResult {
  status: string;
  match_type: string | null;
  similarity_score: number;
  response: string;
  latency_ms: number;
  source: string;
  original_query?: string;
  closest_query?: string | null;
}

// ── API calls ────────────────────────────────────────────────────────────────

export const api = {
  health: () => apiFetch<{ status: string; database: string; llm: string; model: string }>('/api/health'),

  metrics: () => apiFetch<Metrics>('/api/metrics'),

  cache: () => apiFetch<{ total_entries: number; entries: CacheEntry[] }>('/api/cache'),

  history: (limit = 50) => apiFetch<{ history: HistoryEntry[] }>(`/api/history?limit=${limit}`),

  settings: () => apiFetch<Settings>('/api/settings'),

  setThreshold: (threshold: number) =>
    apiFetch('/api/settings/threshold', {
      method: 'PUT',
      body: JSON.stringify({ threshold })
    }),

  setTTL: (ttl_seconds: number) =>
    apiFetch('/api/settings/ttl', {
      method: 'PUT',
      body: JSON.stringify({ ttl_seconds })
    }),

  setModel: (model: string) =>
    apiFetch('/api/settings/model', {
      method: 'PUT',
      body: JSON.stringify({ model })
    }),

  cleanupCache: () =>
    apiFetch<{ status: string; deleted_expired_count: number }>('/api/cache/cleanup', {
      method: 'POST'
    }),

  query: (question: string, messages?: { role: string; content: string }[]) =>
    apiFetch<QueryResult>('/api/query', {
      method: 'POST',
      body: JSON.stringify({ question, messages })
    }),

  store: (question: string, answer: string) =>
    apiFetch('/api/store', {
      method: 'POST',
      body: JSON.stringify({ question, answer })
    }),

  clearCache: () => apiFetch('/api/cache', { method: 'DELETE' }),

  benchmark: () =>
    apiFetch<{
      trials: number;
      original_avg_ms: number;
      optimized_avg_ms: number;
      speedup_factor: number;
      hit_trial_ms: number[];
    }>('/api/benchmark', { method: 'POST' }),

  feedback: (query_hash: string, is_positive: boolean) =>
    apiFetch('/api/feedback', {
      method: 'POST',
      body: JSON.stringify({ query_hash, is_positive })
    })
};
