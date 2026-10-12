'use client';

import React, { useEffect, useState } from 'react';
import { SidebarTrigger } from '../ui/sidebar';
import { Separator } from '../ui/separator';
import { Breadcrumbs } from '../breadcrumbs';
import { ThemeModeToggle } from '../themes/theme-mode-toggle';
import { getBaseUrl } from '@/lib/api';

interface HealthState {
  redis: 'ok' | 'error' | 'loading';
  db: 'ok' | 'error' | 'loading';
  llm: 'ok' | 'error' | 'loading';
  llm_model: string;
  cache_size: number;
  offline_mode: boolean;
  circuit_breaker_active: boolean;
}

function StatusPill({ label, status }: { label: string; status: 'ok' | 'error' | 'loading' }) {
  const colors = {
    ok: 'text-zinc-300',
    error: 'text-rose-400',
    loading: 'text-zinc-500',
  };
  const dotColors = {
    ok: 'bg-emerald-400/80',
    error: 'bg-rose-400/80',
    loading: 'bg-zinc-500 animate-pulse',
  };
  return (
    <span
      className={`flex items-center gap-1.5 text-[10px] font-medium px-2.5 py-0.5 rounded-full bg-white/[0.04] border border-white/[0.08] ${colors[status]}`}
      title={`${label}: ${status}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dotColors[status]}`} />
      {label}
    </span>
  );
}

export default function Header() {
  const [health, setHealth] = useState<HealthState>({
    redis: 'loading',
    db: 'loading',
    llm: 'loading',
    llm_model: '...',
    cache_size: 0,
    offline_mode: false,
    circuit_breaker_active: false,
  });

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const apiUrl = getBaseUrl();
        const [healthRes, metricsRes] = await Promise.all([
          fetch(`${apiUrl}/api/health`, { cache: 'no-store' }),
          fetch(`${apiUrl}/api/metrics`, { cache: 'no-store' }),
        ]);

        if (!healthRes.ok) throw new Error('health endpoint failed');
        const hData = await healthRes.json();
        const mData = metricsRes.ok ? await metricsRes.json() : {};

        setHealth({
          redis: hData.database === 'ok' ? 'ok' : 'error',
          db: hData.database === 'ok' ? 'ok' : 'error',
          llm: hData.llm === 'ok' ? 'ok' : 'error',
          llm_model: hData.llm_model || 'unknown',
          cache_size: mData.cache_size || 0,
          offline_mode: Boolean(hData.offline_mode),
          circuit_breaker_active: Boolean(hData.circuit_breaker?.is_open),
        });
      } catch {
        setHealth((prev) => ({ ...prev, redis: 'error', db: 'error', llm: 'error' }));
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 8000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className='bg-background/70 sticky top-0 z-20 flex h-14 shrink-0 items-center justify-between gap-2 backdrop-blur-xl border-b border-black/[0.05] dark:border-white/[0.08] transition-all'>
      <div className='flex items-center gap-2 px-4'>
        <SidebarTrigger className='-ml-1 rounded-lg hover:bg-muted/60 transition-colors' />
        <Separator orientation='vertical' className='mr-2 h-4 data-vertical:self-center opacity-40' />
        <Breadcrumbs />
      </div>

      <div className='flex items-center gap-2 px-4'>
        {/* Live Infrastructure Health Pills */}
        <div className='hidden sm:flex items-center gap-1.5 mr-2'>
          {health.circuit_breaker_active && (
            <span
              className='flex items-center gap-1.5 text-[10px] font-medium px-2.5 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-300'
              title='Circuit Breaker: Auto-switched to Local LLM due to weak network'
            >
              <span className='w-1.5 h-1.5 rounded-full bg-amber-400/80' />
              Auto-Offline
            </span>
          )}

          <StatusPill label='pgvector' status={health.db} />
          <StatusPill
            label={health.cache_size > 0 ? `${health.cache_size} Vectors` : 'Cache'}
            status={health.db}
          />
          <StatusPill
            label={health.llm === 'ok' ? health.llm_model.split('/').pop() || 'LLM' : 'LLM Offline'}
            status={health.llm}
          />
        </div>
        <ThemeModeToggle />
      </div>
    </header>
  );
}
