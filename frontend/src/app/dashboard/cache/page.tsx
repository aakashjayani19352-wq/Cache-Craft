'use client';

import React, { useState, useEffect, useMemo } from 'react';
import PageContainer from '@/components/layout/page-container';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { api, type CacheEntry } from '@/lib/api';
import { 
  Trash2, 
  RefreshCw, 
  Search, 
  Database, 
  Zap, 
  Copy, 
  Check, 
  Flame, 
  Clock, 
  Layers,
  Sparkles
} from 'lucide-react';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';

type FilterTier = 'all' | 'REDIS' | 'POSTGRES';

export default function CachePage() {
  const [entries, setEntries] = useState<CacheEntry[]>([]);
  const [totalEntries, setTotalEntries] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTier, setActiveTier] = useState<FilterTier>('all');
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  async function fetchCache() {
    setIsLoading(true);
    try {
      const data = await api.cache();
      setEntries(data.entries || []);
      setTotalEntries(data.total_entries || (data.entries ? data.entries.length : 0));
    } catch {
      toast.error('Failed to fetch cache entries');
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    fetchCache();
  }, []);

  async function handleClear() {
    if (!confirm('Are you sure you want to completely flush the Redis and Postgres cache?')) return;
    
    try {
      await api.clearCache();
      toast.success('Cache completely flushed across Redis & pgvector');
      fetchCache();
    } catch {
      toast.error('Failed to clear cache');
    }
  }

  const handleCopy = (hash: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedHash(hash);
    toast.success('Copied to clipboard');
    setTimeout(() => setCopiedHash(null), 2000);
  };

  const filteredEntries = useMemo(() => {
    return entries.filter((entry) => {
      const matchesSearch =
        entry.query.toLowerCase().includes(searchQuery.toLowerCase()) ||
        entry.response.toLowerCase().includes(searchQuery.toLowerCase()) ||
        entry.hash.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesTier =
        activeTier === 'all' ||
        (activeTier === 'REDIS' && (entry.source?.toUpperCase().includes('REDIS') || entry.source?.toUpperCase().includes('L1'))) ||
        (activeTier === 'POSTGRES' && (entry.source?.toUpperCase().includes('POSTGRES') || entry.source?.toUpperCase().includes('L2') || entry.source?.toUpperCase().includes('PGVECTOR')));

      return matchesSearch && matchesTier;
    });
  }, [entries, searchQuery, activeTier]);

  return (
    <PageContainer>
      <div className="flex flex-1 flex-col gap-6 max-w-6xl mx-auto w-full pb-8">
        {/* Apple-grade Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-foreground via-foreground/90 to-foreground/70 bg-clip-text text-transparent">
                Cache Explorer
              </h1>
              <Badge variant="secondary" className="rounded-full px-2.5 py-0.5 text-xs font-medium border border-border/50 bg-muted/60">
                {totalEntries} Cached Vectors
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              Inspect, search, and manage high-dimensional vector embeddings and exact hashes.
            </p>
          </div>

          <div className="flex items-center gap-2.5">
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={fetchCache} 
                disabled={isLoading}
                className="rounded-full px-4 border-black/[0.08] dark:border-white/[0.1] shadow-sm backdrop-blur-md hover:bg-muted/60 transition-all text-xs"
              >
                <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </motion.div>

            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button 
                variant="destructive" 
                size="sm" 
                onClick={handleClear} 
                disabled={totalEntries === 0 || isLoading}
                className="rounded-full px-4 shadow-sm shadow-red-500/10 text-xs transition-all"
              >
                <Trash2 className="w-3.5 h-3.5 mr-1.5" />
                Flush Cache
              </Button>
            </motion.div>
          </div>
        </div>

        {/* Controls: Cupertino Search Bar & Segmented Pill Switcher */}
        <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between">
          {/* Search Capsule */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground/60" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter by query, vector ID, or answer..."
              className="pl-9 pr-4 py-5 rounded-2xl bg-card/60 backdrop-blur-xl border border-black/[0.06] dark:border-white/[0.08] shadow-[0_2px_10px_rgba(0,0,0,0.02)] focus-visible:ring-2 focus-visible:ring-blue-500/20 text-xs"
            />
          </div>

          {/* Segmented Filter Pills */}
          <div className="flex p-1 rounded-2xl bg-muted/50 border border-black/[0.04] dark:border-white/[0.06] self-start sm:self-auto backdrop-blur-lg">
            {(
              [
                { id: 'all', label: 'All Tiers', icon: Layers },
                { id: 'REDIS', label: 'Redis L1', icon: Zap },
                { id: 'POSTGRES', label: 'pgvector L2', icon: Database },
              ] as const
            ).map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTier === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTier(tab.id)}
                  className={`relative flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all ${
                    isActive
                      ? 'text-foreground shadow-sm bg-background dark:bg-zinc-800'
                      : 'text-muted-foreground hover:text-foreground hover:bg-background/40'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Entries Grid */}
        <div className="space-y-3">
          {filteredEntries.length === 0 && !isLoading && (
            <motion.div
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="rounded-3xl border border-dashed border-black/[0.08] dark:border-white/[0.1] bg-card/40 backdrop-blur-md">
                <CardContent className="py-16 text-center space-y-3">
                  <div className="w-12 h-12 rounded-2xl bg-blue-500/10 text-blue-500 flex items-center justify-center mx-auto shadow-inner">
                    <Sparkles className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-base">No cached queries found</h3>
                    <p className="text-xs text-muted-foreground max-w-sm mx-auto mt-1">
                      {searchQuery
                        ? 'No entries match your current search criteria. Try a different query.'
                        : 'Your cache is currently fresh. Ask queries in the AI Playground to populate the cache!'}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          <AnimatePresence>
            {filteredEntries.map((entry, index) => {
              const isRedis = entry.source?.toUpperCase().includes('REDIS') || entry.source?.toUpperCase().includes('L1');
              return (
                <motion.div
                  key={entry.full_hash || entry.hash || index}
                  layout
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ type: 'spring', stiffness: 350, damping: 28, delay: Math.min(index * 0.03, 0.3) }}
                >
                  <Card className="group relative rounded-2xl border border-black/[0.06] dark:border-white/[0.08] bg-card/70 hover:bg-card/95 backdrop-blur-2xl transition-all duration-300 shadow-[0_4px_20px_rgba(0,0,0,0.02)] hover:shadow-[0_8px_30px_rgba(0,0,0,0.06)] hover:-translate-y-0.5 overflow-hidden">
                    <CardContent className="p-5 space-y-3">
                      {/* Top Header Row */}
                      <div className="flex items-start justify-between gap-4">
                        <div className="space-y-1 flex-1">
                          <h3 className="text-sm font-semibold tracking-tight text-foreground leading-snug group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                            {entry.query}
                          </h3>
                          <div className="flex items-center gap-2 text-[11px] font-mono text-muted-foreground/70">
                            <span className="bg-muted/70 px-2 py-0.5 rounded-md border border-border/40">
                              ID: {entry.hash}
                            </span>
                            <button
                              onClick={() => handleCopy(entry.hash, entry.hash)}
                              className="hover:text-foreground transition-colors p-1 rounded hover:bg-muted"
                              title="Copy vector ID"
                            >
                              {copiedHash === entry.hash ? (
                                <Check className="w-3 h-3 text-emerald-500" />
                              ) : (
                                <Copy className="w-3 h-3" />
                              )}
                            </button>
                          </div>
                        </div>

                        {/* Status Badges */}
                        <div className="flex shrink-0 items-center gap-2">
                          <Badge
                            variant="outline"
                            className={`rounded-full px-2.5 py-0.5 text-[11px] font-medium border flex items-center gap-1.5 shadow-sm ${
                              isRedis
                                ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20'
                                : 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20'
                            }`}
                          >
                            {isRedis ? <Zap className="w-3 h-3" /> : <Database className="w-3 h-3" />}
                            {entry.source}
                          </Badge>

                          <Badge
                            variant="secondary"
                            className="rounded-full px-2.5 py-0.5 text-[11px] font-medium border border-border/40 flex items-center gap-1 text-muted-foreground"
                          >
                            <Flame className="w-3 h-3 text-orange-500" />
                            {entry.hit_count} {entry.hit_count === 1 ? 'hit' : 'hits'}
                          </Badge>
                        </div>
                      </div>

                      {/* Cached Output Snippet */}
                      <div className="p-3.5 rounded-xl bg-muted/40 dark:bg-zinc-800/40 border border-black/[0.03] dark:border-white/[0.04]">
                        <p className="text-xs text-muted-foreground leading-relaxed line-clamp-2">
                          {entry.response}
                        </p>
                      </div>

                      {/* Footer Details */}
                      <div className="flex items-center justify-between text-[11px] text-muted-foreground/60 pt-1">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          Cached {new Date(entry.created_at).toLocaleString()}
                        </span>
                        <button
                          onClick={() => handleCopy(entry.full_hash || entry.hash, entry.response)}
                          className="hover:text-foreground text-[11px] font-medium flex items-center gap-1 transition-colors group/copy"
                        >
                          <Copy className="w-3 h-3 group-hover/copy:scale-110 transition-transform" />
                          Copy Response
                        </button>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      </div>
    </PageContainer>
  );
}
