'use client';

import React, { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { api, type Settings } from '@/lib/api';
import { 
  Sliders, 
  Check, 
  Info, 
  Database, 
  Server, 
  Cpu, 
  Zap, 
  Sparkles,
  TrendingUp,
  TrendingDown,
  Clock,
  Trash2,
  Globe,
  Bot,
  Loader2,
  Wifi,
  WifiOff,
  AlertTriangle,
  ShieldCheck,
  Copy,
  ExternalLink
} from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

const TTL_PRESETS = [
  { label: '1 Hour', seconds: 3600 },
  { label: '6 Hours', seconds: 21600 },
  { label: '24 Hours', seconds: 86400 },
  { label: '7 Days', seconds: 604800 },
  { label: '30 Days', seconds: 2592000 },
  { label: 'Permanent', seconds: 0 },
];

export default function SettingsClient({ settings }: { settings: Settings }) {
  const [threshold, setThreshold] = useState(settings.similarity_threshold);
  const [savingThreshold, setSavingThreshold] = useState(false);

  const [ttlSeconds, setTtlSeconds] = useState(settings.ttl_seconds ?? 86400);
  const [savingTtl, setSavingTtl] = useState(false);

  const [selectedModel, setSelectedModel] = useState(settings.active_model ?? 'gemini-flash-latest');
  const [savingModel, setSavingModel] = useState(false);

  const [offlineMode, setOfflineMode] = useState(settings.offline_mode ?? false);
  const [savingOffline, setSavingOffline] = useState(false);

  const [cleaning, setCleaning] = useState(false);
  const [tunnelState, setTunnelState] = useState<{
    status: 'active' | 'inactive' | 'error';
    url: string | null;
  }>({ status: 'inactive', url: null });
  const [tunnelLoading, setTunnelLoading] = useState(false);
  const [copiedTunnel, setCopiedTunnel] = useState(false);

  React.useEffect(() => {
    api.tunnelStatus().then((res) => {
      if (res && res.status === 'active' && res.url) {
        setTunnelState({ status: 'active', url: res.url });
      }
    }).catch(() => {});
  }, []);

  async function handleToggleTunnel() {
    setTunnelLoading(true);
    try {
      if (tunnelState.status === 'active') {
        await api.tunnelStop();
        setTunnelState({ status: 'inactive', url: null });
        toast.success('🛑 Cloudflare Tunnel stopped. Remote GPU access disabled.');
      } else {
        toast.info('⚡ Negotiating Cloudflare HTTPS tunnel (~4s)...');
        const res = await api.tunnelStart();
        if (res && res.status === 'active' && res.url) {
          setTunnelState({ status: 'active', url: res.url });
          toast.success(`⚡ Remote GPU Live: ${res.url}`);
        } else {
          toast.error(res?.message || 'Failed to start tunnel');
        }
      }
    } catch (err: any) {
      toast.error(`Tunnel notice: ${err.message}`);
    } finally {
      setTunnelLoading(false);
    }
  }

  function handleCopyTunnelUrl() {
    if (!tunnelState.url) return;
    navigator.clipboard.writeText(tunnelState.url);
    setCopiedTunnel(true);
    toast.success('Tunnel URL copied to clipboard');
    setTimeout(() => setCopiedTunnel(false), 2000);
  }

  async function handleToggleOffline(enabled: boolean) {
    setSavingOffline(true);
    setOfflineMode(enabled);
    try {
      await api.setOfflineMode(enabled);
      toast.success(
        enabled
          ? 'Offline Mode enabled: routing 100% through local Ollama'
          : 'Cloud Mode restored: Gemini Cloud active with local fallback'
      );
    } catch {
      toast.error('Failed to update offline mode');
      setOfflineMode(!enabled);
    } finally {
      setSavingOffline(false);
    }
  }

  async function handleSaveThreshold() {
    setSavingThreshold(true);
    try {
      await api.setThreshold(threshold);
      toast.success(`Similarity threshold updated to ${(threshold * 100).toFixed(0)}%`);
    } catch {
      toast.error('Failed to update threshold');
    } finally {
      setSavingThreshold(false);
    }
  }

  async function handleSaveTtl(seconds: number) {
    setSavingTtl(true);
    setTtlSeconds(seconds);
    try {
      await api.setTTL(seconds);
      const label = TTL_PRESETS.find((p) => p.seconds === seconds)?.label || `${seconds}s`;
      toast.success(`Cache TTL updated to ${label}`);
    } catch {
      toast.error('Failed to update TTL');
    } finally {
      setSavingTtl(false);
    }
  }

  async function handleSelectModel(modelId: string) {
    setSavingModel(true);
    setSelectedModel(modelId);
    try {
      await api.setModel(modelId);
      toast.success(`Active LLM model set to ${modelId}`);
    } catch {
      toast.error('Failed to update LLM model');
    } finally {
      setSavingModel(false);
    }
  }

  async function handleCleanupExpired() {
    setCleaning(true);
    try {
      const res = await api.cleanupCache();
      toast.success(`Purged ${res.deleted_expired_count} expired cache records`);
    } catch {
      toast.error('Failed to purge expired records');
    } finally {
      setCleaning(false);
    }
  }

  const thresholdLabel =
    threshold >= 0.9
      ? 'Very Strict — Near-duplicate queries only'
      : threshold >= 0.75
      ? 'Balanced — High precision with broad semantic recall'
      : threshold >= 0.6
      ? 'Relaxed — Maximum cache hits with possible semantic drift'
      : 'Lenient — Extremely aggressive caching';

  const thresholdColor =
    threshold >= 0.9
      ? 'text-zinc-200 bg-white/[0.08] border-white/[0.15]'
      : threshold >= 0.75
      ? 'text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
      : threshold >= 0.6
      ? 'text-amber-600 dark:text-amber-400 bg-amber-500/10 border-amber-500/20'
      : 'text-orange-600 dark:text-orange-400 bg-orange-500/10 border-orange-500/20';

  const formatTtlDisplay = (secs: number) => {
    if (secs === 0) return 'Never Expires';
    if (secs < 3600) return `${Math.round(secs / 60)} minutes`;
    if (secs < 86400) return `${Math.round(secs / 3600)} hours`;
    return `${Math.round(secs / 86400)} days`;
  };

  const systemSpecs = [
    { label: 'Embedding Model', value: settings.model, icon: Sparkles },
    { label: 'Vector Dimensions', value: `${settings.embedding_dimensions}d`, icon: Cpu },
    { label: 'Cached Vectors', value: `${settings.cache_size} entries`, icon: Database },
    { label: 'Active LLM Engine', value: selectedModel, icon: Server },
    { label: 'Storage Infrastructure', value: 'PostgreSQL 16 (pgvector) + Redis 7', icon: Zap },
    { label: 'Cache Expiration (TTL)', value: formatTtlDisplay(ttlSeconds), icon: Clock },
    { label: 'Backend API Gateway', value: 'http://localhost:8000', icon: Info },
  ];

  const modelsList = settings.available_models || [
    {
      id: 'auto',
      name: 'Auto-Router (Dynamic Prompt-Aware)',
      provider: 'auto',
      type: 'hybrid',
      description: 'Dynamically inspects prompt intent & complexity — switches to best local or cloud model in real time',
    },
    {
      id: 'gemini-flash-latest',
      name: 'Google Gemini Flash (Cloud)',
      provider: 'gemini',
      type: 'cloud',
      description: 'High-speed cloud LLM — primary inference engine with automatic local fallback',
    },
    {
      id: 'qwen2.5:7b',
      name: 'Ollama (Qwen 2.5 — 7B Local)',
      provider: 'ollama',
      type: 'local',
      description: 'Flagship 7B local model on RTX 4060 — state-of-the-art coding, math, and complex reasoning (4.7 GB)',
    },
    {
      id: 'llama3.2',
      name: 'Ollama (Llama 3.2 — 3B Local)',
      provider: 'ollama',
      type: 'local',
      description: 'Ultra-fast 3B local model — instant response time for conversational chit-chat & greetings (2.0 GB)',
    },
  ];

  return (
    <div className="flex flex-1 flex-col gap-6 max-w-5xl mx-auto w-full pb-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-foreground via-foreground/90 to-foreground/70 bg-clip-text text-transparent">
          System Configuration
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Calibrate semantic similarity thresholds, manage cache TTL lifecycles, and select LLM inference providers.
        </p>
      </div>

      {/* Card: Offline Mode & Weak-Network Resilience */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ type: 'spring', stiffness: 350, damping: 28 }}
      >
        <Card className="rounded-3xl border border-black/[0.06] dark:border-white/[0.08] bg-card/70 backdrop-blur-2xl shadow-[0_8px_30px_rgb(0,0,0,0.03)] overflow-hidden">
          <CardHeader className="pb-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className={`p-2.5 rounded-2xl ${offlineMode ? 'bg-amber-500/10 text-amber-500' : 'bg-emerald-500/10 text-emerald-500'}`}>
                  {offlineMode ? <WifiOff className="w-5 h-5" /> : <Wifi className="w-5 h-5" />}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <CardTitle className="text-lg font-bold">Offline Mode & Network Resilience</CardTitle>
                    <Badge variant="outline" className={`rounded-full px-2.5 py-0.5 text-[11px] font-semibold border ${
                      offlineMode 
                        ? 'border-amber-500/30 bg-amber-500/10 text-amber-600 dark:text-amber-400' 
                        : 'border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                    }`}>
                      {offlineMode ? '100% Offline Active' : 'Cloud First + Auto-Fallback'}
                    </Badge>
                  </div>
                  <CardDescription className="text-xs mt-0.5">
                    Instant failover to local GPU models when network is weak, with optional 100% offline air-gapped mode.
                  </CardDescription>
                </div>
              </div>

              <div className="flex items-center gap-2 self-start sm:self-center">
                {settings.circuit_breaker?.is_open && (
                  <Badge variant="outline" className="rounded-full px-2.5 py-1 text-xs font-medium border border-amber-500/30 bg-amber-500/10 text-amber-600 dark:text-amber-400 animate-pulse">
                    <AlertTriangle className="w-3 h-3 mr-1" />
                    Circuit Breaker Active ({settings.circuit_breaker.cooldown_seconds}s)
                  </Badge>
                )}
                <Button
                  variant={offlineMode ? "default" : "outline"}
                  size="sm"
                  disabled={savingOffline}
                  onClick={() => handleToggleOffline(!offlineMode)}
                  className={`rounded-full px-4 text-xs font-semibold transition-all ${
                    offlineMode
                      ? "bg-amber-500 hover:bg-amber-600 text-white shadow-md shadow-amber-500/20"
                      : "border-black/10 dark:border-white/10 hover:bg-muted"
                  }`}
                >
                  {savingOffline ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" />
                  ) : offlineMode ? (
                    <WifiOff className="w-3.5 h-3.5 mr-1.5" />
                  ) : (
                    <Wifi className="w-3.5 h-3.5 mr-1.5" />
                  )}
                  {offlineMode ? 'Active (Click to Restore Cloud)' : 'Switch to Offline Mode'}
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
              <div className="p-3.5 rounded-2xl bg-muted/40 border border-black/[0.04] dark:border-white/[0.06] flex flex-col justify-between">
                <span className="text-[11px] font-medium text-muted-foreground">Active Inference Route</span>
                <span className="text-sm font-bold mt-1 flex items-center gap-1.5">
                  <span className={`w-2 h-2 rounded-full ${offlineMode ? 'bg-amber-500' : 'bg-emerald-500'}`} />
                  {offlineMode ? 'Local Ollama (RTX 4060 GPU)' : 'Gemini Cloud (with Local Fallback)'}
                </span>
              </div>
              <div className="p-3.5 rounded-2xl bg-muted/40 border border-black/[0.04] dark:border-white/[0.06] flex flex-col justify-between">
                <span className="text-[11px] font-medium text-muted-foreground">Weak Network Failover</span>
                <span className="text-sm font-bold mt-1 text-emerald-600 dark:text-emerald-400">
                  3.5s Aggressive Fail-Fast
                </span>
              </div>
              <div className="p-3.5 rounded-2xl bg-muted/40 border border-black/[0.04] dark:border-white/[0.06] flex flex-col justify-between">
                <span className="text-[11px] font-medium text-muted-foreground">Mid-Session Switch</span>
                <span className="text-sm font-bold mt-1 text-zinc-200">
                  Live in Chat & Settings
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Card 1: Similarity Threshold Slider */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ type: 'spring', stiffness: 350, damping: 28 }}
        >
          <Card className="rounded-3xl border border-black/[0.06] dark:border-white/[0.08] bg-card/70 backdrop-blur-2xl shadow-[0_8px_30px_rgb(0,0,0,0.03)] h-full flex flex-col justify-between">
            <CardHeader className="pb-4">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-white/[0.06] text-zinc-200">
                  <Sliders className="w-4 h-4" />
                </div>
                <CardTitle className="text-lg font-bold">Similarity Threshold</CardTitle>
              </div>
              <CardDescription className="text-xs">
                Minimum cosine similarity score required for an incoming query to hit the L2 semantic cache.
              </CardDescription>
            </CardHeader>

            <CardContent className="flex flex-col gap-5 pt-2">
              <div className="flex items-center justify-between p-4 rounded-2xl bg-muted/40 border border-black/[0.04] dark:border-white/[0.06]">
                <div>
                  <span className="text-4xl font-extrabold tracking-tight tabular-nums font-mono">
                    {(threshold * 100).toFixed(0)}%
                  </span>
                  <span className="text-xs text-muted-foreground ml-2">cosine similarity</span>
                </div>

                <Badge variant="outline" className={`rounded-full px-3 py-1 text-xs font-medium border ${thresholdColor}`}>
                  {threshold >= 0.75 ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
                  {thresholdLabel.split('—')[0].trim()}
                </Badge>
              </div>

              <div className="space-y-3 px-1">
                <Slider
                  min={0.3}
                  max={0.99}
                  step={0.01}
                  value={[threshold]}
                  onValueChange={(val) => {
                    const v = Array.isArray(val) ? val[0] : (typeof val === 'number' ? val : 0.85);
                    if (v !== undefined) setThreshold(v);
                  }}
                  className="py-2 cursor-pointer"
                />

                <div className="flex justify-between text-[11px] text-muted-foreground/75 font-mono">
                  <span>30% (Lenient)</span>
                  <span>75% (Recommended)</span>
                  <span>99% (Strict)</span>
                </div>
              </div>

              <div className="p-3.5 rounded-2xl bg-white/[0.03] border border-white/[0.08] text-xs text-muted-foreground space-y-1">
                <p className="font-semibold text-foreground/90 flex items-center gap-1.5">
                  <Info className="w-3.5 h-3.5 text-zinc-400" />
                  {thresholdLabel}
                </p>
                <p className="text-[11px] leading-relaxed">
                  Queries with semantic cosine vector distance above {(threshold * 100).toFixed(0)}% are served instantly from pgvector in under 25ms.
                </p>
              </div>

              <motion.div whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}>
                <Button
                  onClick={handleSaveThreshold}
                  disabled={savingThreshold}
                  className="w-full rounded-2xl py-5 bg-zinc-100 hover:bg-white text-zinc-950 font-medium text-sm transition-all shadow-sm"
                >
                  {savingThreshold ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Applying Threshold...
                    </>
                  ) : (
                    <>
                      <Check className="w-4 h-4 mr-2" />
                      Save Threshold
                    </>
                  )}
                </Button>
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Card 2: Cache TTL Expiration Controls */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ type: 'spring', stiffness: 350, damping: 28, delay: 0.05 }}
        >
          <Card className="rounded-3xl border border-black/[0.06] dark:border-white/[0.08] bg-card/70 backdrop-blur-2xl shadow-[0_8px_30px_rgb(0,0,0,0.03)] h-full flex flex-col justify-between">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-xl bg-amber-500/10 text-amber-500">
                    <Clock className="w-4 h-4" />
                  </div>
                  <CardTitle className="text-lg font-bold">Cache TTL Lifecycle</CardTitle>
                </div>
                <Badge variant="outline" className="rounded-full px-2.5 py-0.5 text-[11px] font-mono border-amber-500/30 text-amber-500 bg-amber-500/5">
                  {formatTtlDisplay(ttlSeconds)}
                </Badge>
              </div>
              <CardDescription className="text-xs">
                Automatic time-to-live duration for Redis keys and PostgreSQL vector entries before expiration.
              </CardDescription>
            </CardHeader>

            <CardContent className="flex flex-col gap-4 pt-2">
              <div className="grid grid-cols-3 gap-2">
                {TTL_PRESETS.map((p) => {
                  const isSelected = ttlSeconds === p.seconds;
                  return (
                    <button
                      key={p.label}
                      onClick={() => handleSaveTtl(p.seconds)}
                      disabled={savingTtl}
                      className={`p-3 rounded-2xl border text-xs font-medium transition-all text-center flex flex-col items-center justify-center gap-1 ${
                        isSelected
                          ? 'bg-amber-500/15 border-amber-500/40 text-amber-600 dark:text-amber-400 shadow-sm'
                          : 'bg-muted/30 border-border/40 hover:bg-muted/70 text-muted-foreground'
                      }`}
                    >
                      <span className="font-semibold">{p.label}</span>
                      <span className="text-[10px] opacity-75 font-mono">
                        {p.seconds === 0 ? 'Infinite' : `${p.seconds}s`}
                      </span>
                    </button>
                  );
                })}
              </div>

              <div className="p-3.5 rounded-2xl bg-amber-500/[0.04] border border-amber-500/15 text-xs text-muted-foreground space-y-1">
                <p className="font-semibold text-foreground/90 flex items-center gap-1.5">
                  <Info className="w-3.5 h-3.5 text-amber-500" />
                  Dual-Tier Expiration
                </p>
                <p className="text-[11px] leading-relaxed">
                  Redis applies native key expiry (`EX {ttlSeconds || 'nil'}`). PostgreSQL indexes entries with `expires_at` and automatically excludes stale records.
                </p>
              </div>

              <div className="pt-2">
                <Button
                  variant="outline"
                  onClick={handleCleanupExpired}
                  disabled={cleaning}
                  className="w-full rounded-2xl py-5 border-border/60 hover:bg-red-500/10 hover:text-red-500 hover:border-red-500/30 text-xs transition-all flex items-center justify-center gap-2"
                >
                  {cleaning ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Trash2 className="w-3.5 h-3.5" />
                  )}
                  Purge Expired Database Records
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Card 3: Model Selection */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ type: 'spring', stiffness: 350, damping: 28, delay: 0.1 }}
        >
          <Card className="rounded-3xl border border-black/[0.06] dark:border-white/[0.08] bg-card/70 backdrop-blur-2xl shadow-[0_8px_30px_rgb(0,0,0,0.03)] h-full flex flex-col justify-between">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-xl bg-white/[0.06] text-zinc-200">
                    <Bot className="w-4 h-4" />
                  </div>
                  <CardTitle className="text-lg font-bold">LLM Inference Engine</CardTitle>
                </div>
                <Badge variant="secondary" className="rounded-full text-[10px] px-2 py-0.5">
                  Pluggable Provider
                </Badge>
              </div>
              <CardDescription className="text-xs">
                Switch between local offline Ollama models and Google Gemini Cloud fallback.
              </CardDescription>
            </CardHeader>

            <CardContent className="flex flex-col gap-3 pt-2">
              <div className="space-y-2">
                {modelsList.map((m) => {
                  const isSelected = selectedModel === m.id;
                  const isLocal = m.type === 'local';
                  return (
                    <button
                      key={m.id}
                      onClick={() => handleSelectModel(m.id)}
                      disabled={savingModel}
                      className={`w-full p-3.5 rounded-2xl border text-left transition-all flex items-center justify-between ${
                        isSelected
                          ? 'bg-white/[0.08] border-white/[0.2] text-foreground shadow-sm'
                          : 'bg-muted/20 border-border/40 hover:bg-muted/50 text-muted-foreground'
                      }`}
                    >
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-semibold text-foreground">{m.name}</span>
                          <Badge
                            variant="outline"
                            className={`text-[9px] px-1.5 py-0 rounded-md font-mono ${
                              isLocal ? 'border-emerald-500/40 text-emerald-500' : 'border-white/[0.15] text-zinc-300'
                            }`}
                          >
                            {isLocal ? '100% Offline' : 'Cloud LLM'}
                          </Badge>
                        </div>
                        <p className="text-[11px] text-muted-foreground">{m.description}</p>
                      </div>

                      {isSelected && (
                        <div className="p-1 rounded-full bg-zinc-200 text-zinc-950">
                          <Check className="w-3 h-3" />
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>

              <div className="p-3 rounded-2xl bg-white/[0.03] border border-white/[0.08] text-[11px] text-muted-foreground space-y-1">
                <span className="font-semibold text-foreground/90 flex items-center gap-1.5">
                  <Globe className="w-3.5 h-3.5 text-zinc-400" />
                  Automatic Cloud-to-Local Resilience
                </span>
                <p className="leading-relaxed">
                  If Google Gemini experiences quota limits, 503 spikes, or network outages, the system seamlessly redirects to local Ollama with zero interruption.
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Card 4: Engine Specifications */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ type: 'spring', stiffness: 350, damping: 28, delay: 0.15 }}
        >
          <Card className="rounded-3xl border border-black/[0.06] dark:border-white/[0.08] bg-card/70 backdrop-blur-2xl shadow-[0_8px_30px_rgb(0,0,0,0.03)] h-full">
            <CardHeader className="pb-4">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-white/[0.06] text-zinc-200">
                  <Cpu className="w-4 h-4" />
                </div>
                <CardTitle className="text-lg font-bold">Engine Specifications</CardTitle>
              </div>
              <CardDescription className="text-xs">
                Real-time active hardware, vector indices, and runtime nodes.
              </CardDescription>
            </CardHeader>

            <CardContent className="pt-2">
              <div className="divide-y divide-border/40">
                {systemSpecs.map((item) => {
                  const Icon = item.icon;
                  return (
                    <div key={item.label} className="flex items-center justify-between py-3 first:pt-0 last:pb-0">
                      <div className="flex items-center gap-2.5">
                        <div className="p-1.5 rounded-lg bg-muted/60 text-muted-foreground">
                          <Icon className="w-3.5 h-3.5" />
                        </div>
                        <span className="text-xs font-medium text-muted-foreground">{item.label}</span>
                      </div>
                      <span className="text-xs font-mono font-medium text-foreground bg-muted/40 px-2.5 py-1 rounded-lg border border-border/30">
                        {item.value}
                      </span>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </motion.div>
        {/* Card 5: Cloudflare Remote GPU Tunnel */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ type: 'spring', stiffness: 350, damping: 28, delay: 0.2 }}
          className="lg:col-span-2"
        >
          <Card className="rounded-3xl border border-black/[0.06] dark:border-white/[0.08] bg-card/70 backdrop-blur-2xl shadow-[0_8px_30px_rgb(0,0,0,0.03)] overflow-hidden">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-xl bg-white/[0.06] text-zinc-200">
                    <Globe className="w-4 h-4" />
                  </div>
                  <div>
                    <CardTitle className="text-lg font-bold">Cloudflare Remote GPU Tunnel</CardTitle>
                    <CardDescription className="text-xs">
                      Enable or disable public HTTPS routing to your laptop&apos;s physical RTX 4060 GPU with 1 click.
                    </CardDescription>
                  </div>
                </div>

                <Badge
                  variant="outline"
                  className={`rounded-full px-3 py-1 text-xs font-mono flex items-center gap-1.5 ${
                    tunnelState.status === 'active'
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      : 'bg-white/[0.04] text-zinc-400 border-white/[0.08]'
                  }`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      tunnelState.status === 'active' ? 'bg-emerald-400' : 'bg-zinc-500'
                    }`}
                  />
                  <span>
                    {tunnelState.status === 'active'
                      ? 'Tunnel Active · GPU Exposed'
                      : 'Tunnel Inactive · Private Local Only'}
                  </span>
                </Badge>
              </div>
            </CardHeader>

            <CardContent className="space-y-4 pt-1">
              <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div className="space-y-1.5 max-w-xl">
                  <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200">
                    <Cpu className="w-3.5 h-3.5 text-zinc-400" />
                    <span>NVIDIA GeForce RTX 4060 Laptop GPU (8GB)</span>
                  </div>
                  <p className="text-[11px] text-muted-foreground leading-relaxed">
                    {tunnelState.status === 'active'
                      ? 'Anyone visiting cache-craft.vercel.app or querying from a phone on cellular data will be routed to your physical laptop GPU.'
                      : 'When disabled, your GPU is completely private and only reachable on your local machine or home Wi-Fi. Turn this on only when you want remote visitors or judges to test your laptop.'}
                  </p>
                  {tunnelState.url && (
                    <div className="flex items-center gap-2 pt-2">
                      <span className="text-xs font-mono text-zinc-200 bg-white/[0.05] border border-white/[0.08] px-3 py-1 rounded-xl truncate max-w-md">
                        {tunnelState.url}
                      </span>
                      <button
                        type="button"
                        onClick={handleCopyTunnelUrl}
                        className="p-1.5 rounded-lg bg-white/[0.06] hover:bg-white/[0.12] text-zinc-300 transition-colors"
                        title="Copy Tunnel URL"
                      >
                        {copiedTunnel ? <Check className="w-3.5 h-3.5 text-zinc-200" /> : <Copy className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  )}
                </div>

                <Button
                  onClick={handleToggleTunnel}
                  disabled={tunnelLoading}
                  className={`rounded-2xl px-5 py-5 text-xs font-semibold transition-all shrink-0 ${
                    tunnelState.status === 'active'
                      ? 'bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 shadow-none'
                      : 'bg-zinc-100 hover:bg-white text-zinc-950 shadow-sm'
                  }`}
                >
                  {tunnelLoading ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 mr-2 animate-spin" />
                      {tunnelState.status === 'active' ? 'Stopping Tunnel...' : 'Negotiating Tunnel...'}
                    </>
                  ) : tunnelState.status === 'active' ? (
                    'Disable Remote Tunnel'
                  ) : (
                    'Enable Remote GPU Tunnel →'
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
