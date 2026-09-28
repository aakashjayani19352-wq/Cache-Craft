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
  Loader2
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

  const [selectedModel, setSelectedModel] = useState(settings.active_model ?? 'llama3.2');
  const [savingModel, setSavingModel] = useState(false);

  const [cleaning, setCleaning] = useState(false);

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
      ? 'text-indigo-600 dark:text-indigo-400 bg-indigo-500/10 border-indigo-500/20'
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
      id: 'llama3.2',
      name: 'Ollama (llama3.2 — 3B Local)',
      provider: 'ollama',
      type: 'local',
      description: 'Fast, private, 100% offline local inference',
    },
    {
      id: 'gemini-3.8-flash',
      name: 'Google Gemini 3.8 Flash (Cloud)',
      provider: 'gemini',
      type: 'cloud',
      description: 'High-speed cloud LLM with automatic local fallback',
    }
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
                <div className="p-2 rounded-xl bg-blue-500/10 text-blue-500">
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
                  onValueChange={([v]) => setThreshold(v)}
                  className="py-2 cursor-pointer"
                />

                <div className="flex justify-between text-[11px] text-muted-foreground/75 font-mono">
                  <span>30% (Lenient)</span>
                  <span>75% (Recommended)</span>
                  <span>99% (Strict)</span>
                </div>
              </div>

              <div className="p-3.5 rounded-2xl bg-blue-500/[0.04] border border-blue-500/15 text-xs text-muted-foreground space-y-1">
                <p className="font-semibold text-foreground/90 flex items-center gap-1.5">
                  <Info className="w-3.5 h-3.5 text-blue-500" />
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
                  className="w-full rounded-2xl py-5 bg-blue-600 hover:bg-blue-500 text-white font-medium shadow-md shadow-blue-500/20 text-sm transition-all"
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
                  <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-500">
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
                          ? 'bg-indigo-500/10 border-indigo-500/40 text-foreground shadow-sm'
                          : 'bg-muted/20 border-border/40 hover:bg-muted/50 text-muted-foreground'
                      }`}
                    >
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-semibold text-foreground">{m.name}</span>
                          <Badge
                            variant="outline"
                            className={`text-[9px] px-1.5 py-0 rounded-md font-mono ${
                              isLocal ? 'border-emerald-500/40 text-emerald-500' : 'border-blue-500/40 text-blue-500'
                            }`}
                          >
                            {isLocal ? '100% Offline' : 'Cloud LLM'}
                          </Badge>
                        </div>
                        <p className="text-[11px] text-muted-foreground">{m.description}</p>
                      </div>

                      {isSelected && (
                        <div className="p-1 rounded-full bg-indigo-500 text-white">
                          <Check className="w-3 h-3" />
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>

              <div className="p-3 rounded-2xl bg-indigo-500/[0.04] border border-indigo-500/15 text-[11px] text-muted-foreground space-y-1">
                <span className="font-semibold text-foreground/90 flex items-center gap-1.5">
                  <Globe className="w-3.5 h-3.5 text-indigo-500" />
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
                <div className="p-2 rounded-xl bg-purple-500/10 text-purple-500">
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
      </div>
    </div>
  );
}
