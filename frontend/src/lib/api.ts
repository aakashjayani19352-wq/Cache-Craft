/**
 * api.ts — Cache-Craft Backend API Client
 * All calls to http://localhost:8000
 */

export function getBaseUrl(): string {
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    const isLanOrLocal =
      hostname === 'localhost' ||
      hostname === '127.0.0.1' ||
      /^192\.168\./.test(hostname) ||
      /^10\./.test(hostname) ||
      /^172\.(1[6-9]|2\d|3[01])\./.test(hostname);
    if (isLanOrLocal) {
      return `${window.location.protocol}//${hostname}:8000`;
    }
    if (process.env.NEXT_PUBLIC_API_URL) {
      return process.env.NEXT_PUBLIC_API_URL.replace(/\/+$/, '');
    }
    // In cloud production (e.g. Vercel) when NEXT_PUBLIC_API_URL is omitted,
    // fallback to relative path so same-origin proxy handles /api without Mixed Content errors
    return '';
  }
  return (process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000').replace(/\/+$/, '');
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const base = getBaseUrl();
  const res = await fetch(`${base}${path}`, {
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
  offline_mode?: boolean;
  preferred_local_model?: string;
  circuit_breaker?: {
    is_open: boolean;
    cooldown_seconds: number;
    reason: string | null;
  };
  cache_size: number;
  model: string;
  embedding_dimensions: number;
  gpu_access_allowed?: boolean;
  gpu_access_message?: string;
}

export interface QueryResult {
  status: string;
  match_type: string | null;
  similarity_score: number;
  response: string;
  latency_ms: number;
  source: string;
  query_hash?: string;
  similarity_threshold?: number;
  original_query?: string;
  closest_query?: string | null;
  offline_mode?: boolean;
  fallback_triggered?: boolean;
  fallback_reason?: string | null;
  note?: string | null;
  routed_model?: string | null;
  router_category?: string | null;
  router_reason?: string | null;
}

// ── API calls ────────────────────────────────────────────────────────────────

export const api = {
  health: () => apiFetch<{ status: string; database: string; llm: string; model: string; offline_mode?: boolean; circuit_breaker?: { is_open: boolean; cooldown_seconds: number; reason: string | null } }>('/api/health'),

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

  setOfflineMode: (offline_mode: boolean, preferred_local_model?: string) =>
    apiFetch('/api/settings/offline-mode', {
      method: 'PUT',
      body: JSON.stringify({ offline_mode, preferred_local_model })
    }),

  getGpuAccess: (simulateGuest?: boolean) =>
    apiFetch<{
      gpu_access_allowed: boolean;
      is_creator_device: boolean;
      client_ip: string;
      message: string;
    }>(`/api/system/gpu-access${simulateGuest ? '?guest=1' : ''}`),

  preloadModel: (model: string = 'qwen2.5:7b') =>
    apiFetch<{
      status: string;
      model: string;
      vram_loaded: boolean;
      vram_size_bytes?: number;
      vram_size_formatted?: string;
      load_time_ms?: number;
      device?: string;
      message?: string;
    }>(`/api/models/preload?model=${encodeURIComponent(model)}`, {
      method: 'POST'
    }),

  tunnelStatus: () =>
    apiFetch<{
      status: 'active' | 'inactive' | 'error';
      url: string | null;
      target?: string;
      device?: string;
      message?: string;
    }>('/api/tunnel/status'),

  tunnelStart: () =>
    apiFetch<{
      status: 'active' | 'inactive' | 'error';
      url: string | null;
      target?: string;
      device?: string;
      message?: string;
    }>('/api/tunnel/start', {
      method: 'POST'
    }),

  tunnelStop: () =>
    apiFetch<{
      status: 'active' | 'inactive' | 'error';
      url: string | null;
      message?: string;
    }>('/api/tunnel/stop', {
      method: 'POST'
    }),

  cleanupCache: () =>
    apiFetch<{ status: string; deleted_expired_count: number }>('/api/cache/cleanup', {
      method: 'POST'
    }),

  query: (question: string, messages?: { role: string; content: string }[], offline_mode?: boolean, model?: string) =>
    apiFetch<QueryResult>('/api/query', {
      method: 'POST',
      body: JSON.stringify({ question, messages, offline_mode, model })
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
    }),

  deleteEntry: (query_hash: string) =>
    apiFetch<{ status: string; query_hash: string }>(`/api/cache/${query_hash}`, {
      method: 'DELETE'
    })
};
