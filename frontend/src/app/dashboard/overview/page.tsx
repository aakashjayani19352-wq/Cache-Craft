'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Zap, 
  Server, 
  Activity, 
  TrendingUp, 
  Clock, 
  Cpu, 
  Database, 
  Layers,
  ArrowRight,
  ShieldCheck
} from 'lucide-react';
import { motion } from 'framer-motion';

interface Metrics {
  total_queries: number;
  cache_hits: number;
  cache_misses: number;
  hit_rate_percent: number;
  avg_hit_latency_ms: number;
  avg_miss_latency_ms: number;
  cost_savings_percent: number;
  cache_size: number;
  similarity_threshold: number;
}

export default function OverviewPage() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/metrics');
        if (!res.ok) throw new Error('Network response was not ok');
        const data = await res.json();
        setMetrics(data);
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 4000); // Live polling
    return () => clearInterval(interval);
  }, []);

  if (loading && !metrics) {
    return (
      <div className="flex h-[80vh] w-full items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-blue-500 border-t-transparent animate-spin" />
          <p className="text-xs text-muted-foreground font-medium tracking-wide">Connecting to Cache-Craft cluster...</p>
        </div>
      </div>
    );
  }

  const kpis = [
    {
      title: 'Total Queries Routed',
      value: (metrics?.total_queries || 0).toLocaleString(),
      subtitle: `${metrics?.cache_hits || 0} hits · ${metrics?.cache_misses || 0} misses`,
      icon: Activity,
      color: 'text-blue-500',
      bg: 'bg-blue-500/10 border-blue-500/20',
      gradient: 'from-blue-500/10 to-transparent'
    },
    {
      title: 'Global Hit Rate',
      value: `${metrics?.hit_rate_percent || 0}%`,
      subtitle: 'Combined L1 & L2 efficiency',
      icon: Zap,
      color: 'text-emerald-500',
      bg: 'bg-emerald-500/10 border-emerald-500/20',
      gradient: 'from-emerald-500/10 to-transparent'
    },
    {
      title: 'Estimated Cost Savings',
      value: `${metrics?.cost_savings_percent || 0}%`,
      subtitle: 'LLM inference tokens eliminated',
      icon: TrendingUp,
      color: 'text-purple-500',
      bg: 'bg-purple-500/10 border-purple-500/20',
      gradient: 'from-purple-500/10 to-transparent'
    },
    {
      title: 'Avg Cache Latency',
      value: `${metrics?.avg_hit_latency_ms || 0}ms`,
      subtitle: `vs ${metrics?.avg_miss_latency_ms || 2500}ms LLM cold path`,
      icon: Clock,
      color: 'text-amber-500',
      bg: 'bg-amber-500/10 border-amber-500/20',
      gradient: 'from-amber-500/10 to-transparent'
    }
  ];

  return (
    <div className="flex-1 space-y-8 p-4 sm:p-8 max-w-7xl mx-auto pb-12">
      {/* Apple-grade Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-foreground via-foreground/90 to-foreground/70 bg-clip-text text-transparent">
            System Analytics
          </h1>
          <p className="text-sm text-muted-foreground">
            Real-time telemetry and multi-tier caching performance metrics.
          </p>
        </div>

        {/* Live Status Capsule */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-xs font-medium backdrop-blur-md shadow-sm">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            Cluster Active & Routing
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {kpis.map((kpi, i) => (
          <motion.div
            key={kpi.title}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ type: 'spring', stiffness: 350, damping: 28, delay: i * 0.05 }}
            whileHover={{ y: -3, transition: { duration: 0.2 } }}
          >
            <Card className="relative overflow-hidden rounded-3xl border border-black/[0.06] dark:border-white/[0.08] bg-card/70 hover:bg-card/90 backdrop-blur-2xl shadow-[0_8px_30px_rgb(0,0,0,0.03)] hover:shadow-[0_12px_36px_rgba(0,0,0,0.06)] transition-all">
              <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${kpi.gradient} rounded-full blur-2xl pointer-events-none`} />
              <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                <CardTitle className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  {kpi.title}
                </CardTitle>
                <div className={`p-2.5 rounded-2xl border ${kpi.bg}`}>
                  <kpi.icon className={`w-4 h-4 ${kpi.color}`} />
                </div>
              </CardHeader>
              <CardContent className="space-y-1">
                <div className="text-3xl font-bold tracking-tight">{kpi.value}</div>
                <p className="text-[11px] text-muted-foreground/80 font-medium">
                  {kpi.subtitle}
                </p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Visual Multi-Tier Architecture Pipeline */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ type: 'spring', stiffness: 350, damping: 28, delay: 0.25 }}
      >
        <Card className="rounded-3xl border border-black/[0.06] dark:border-white/[0.08] bg-card/70 backdrop-blur-2xl shadow-[0_8px_30px_rgb(0,0,0,0.03)] overflow-hidden">
          <CardHeader className="border-b border-border/40 pb-4">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg font-bold tracking-tight">
                  Multi-Tier Routing Pipeline
                </CardTitle>
                <p className="text-xs text-muted-foreground mt-0.5">
                  How every incoming query traverses the semantic cache hierarchy
                </p>
              </div>
              <Badge variant="outline" className="rounded-full text-xs font-mono font-normal">
                Cosine Threshold: {((metrics?.similarity_threshold || 0.8) * 100).toFixed(0)}%
              </Badge>
            </div>
          </CardHeader>

          <CardContent className="p-6">
            <div className="grid gap-4 lg:grid-cols-3">
              {/* L1 Tier */}
              <div className="relative p-5 rounded-2xl bg-gradient-to-b from-emerald-500/[0.04] to-transparent border border-emerald-500/20 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-500">
                      <Zap className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-foreground">Tier 1: Redis RAM</h4>
                      <p className="text-[11px] text-muted-foreground">In-Memory Hash Ring</p>
                    </div>
                  </div>
                  <Badge variant="secondary" className="rounded-full text-[10px] bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-mono">
                    ~0.5ms - 1ms
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  O(1) exact match lookup via SHA-256 hash. Queries identical to prior queries return instantaneously with 0 inference cost.
                </p>
                <div className="pt-2 flex items-center gap-1.5 text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Exact Match Layer</span>
                </div>
              </div>

              {/* L2 Tier */}
              <div className="relative p-5 rounded-2xl bg-gradient-to-b from-blue-500/[0.04] to-transparent border border-blue-500/20 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <div className="p-2 rounded-xl bg-blue-500/10 text-blue-500">
                      <Database className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-foreground">Tier 2: pgvector</h4>
                      <p className="text-[11px] text-muted-foreground">PostgreSQL Semantic Store</p>
                    </div>
                  </div>
                  <Badge variant="secondary" className="rounded-full text-[10px] bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20 font-mono">
                    ~15ms - 30ms
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Deep sentence-transformer vector embedding compared against index using cosine similarity. Catches rephrased queries.
                </p>
                <div className="pt-2 flex items-center gap-1.5 text-[11px] text-blue-600 dark:text-blue-400 font-medium">
                  <Layers className="w-3.5 h-3.5" />
                  <span>Semantic Vector Match</span>
                </div>
              </div>

              {/* L3 Tier */}
              <div className="relative p-5 rounded-2xl bg-gradient-to-b from-amber-500/[0.04] to-transparent border border-amber-500/20 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <div className="p-2 rounded-xl bg-amber-500/10 text-amber-500">
                      <Cpu className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-foreground">Tier 3: Ollama LLM</h4>
                      <p className="text-[11px] text-muted-foreground">Cold Path Generation</p>
                    </div>
                  </div>
                  <Badge variant="secondary" className="rounded-full text-[10px] bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 font-mono">
                    {metrics?.avg_miss_latency_ms || 2500}ms
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Invoked only when both L1 and L2 miss. Generates a fresh response via local LLM, then automatically back-fills L1 and L2!
                </p>
                <div className="pt-2 flex items-center gap-1.5 text-[11px] text-amber-600 dark:text-amber-400 font-medium">
                  <Server className="w-3.5 h-3.5" />
                  <span>Generative Cold Fallback</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
