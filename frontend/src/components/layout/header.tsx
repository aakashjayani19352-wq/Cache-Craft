'use client';

import React, { useEffect, useState } from 'react';
import { SidebarTrigger } from '../ui/sidebar';
import { Separator } from '../ui/separator';
import { Breadcrumbs } from '../breadcrumbs';
import { ThemeModeToggle } from '../themes/theme-mode-toggle';

interface HealthState {
  redis: 'ok' | 'error' | 'loading';
  db: 'ok' | 'error' | 'loading';
  llm: 'ok' | 'error' | 'loading';
  llm_model: string;
  cache_size: number;
}

function StatusPill({ label, status }: { label: string; status: 'ok' | 'error' | 'loading' }) {
  const colors = {
    ok: 'text-emerald-600 dark:text-emerald-400',
    error: 'text-red-500 dark:text-red-400',
    loading: 'text-muted-foreground',
  };
  const dotColors = {
    ok: 'bg-emerald-500 shadow-[0_0_6px_rgba(16,185,129,0.7)]',
    error: 'bg-red-500 shadow-[0_0_6px_rgba(239,68,68,0.7)]',
    loading: 'bg-zinc-400 animate-pulse',
  };
  return (
    <span
      className={`flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded-full bg-muted/50 border border-border/40 ${colors[status]}`}
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
  });

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
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
