import { Card, CardHeader, CardContent, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { HistoryEntry } from '@/lib/api';

const STATUS_STYLES: Record<string, string> = {
  CACHE_HIT: 'bg-emerald-500/15 text-emerald-600 border-emerald-500/30',
  CACHE_MISS: 'bg-orange-500/15 text-orange-600 border-orange-500/30'
};

const TIER_SHORT: Record<string, string> = {
  'L0 (In-Memory LRU Cache)': 'L0',
  'L0 (Memory LRU)': 'L0',
  'L1 (Hash Lookup)': 'L1',
  'L1 (Hash Lookup - Database)': 'L1',
  'L2 (Vector Search - Database)': 'L2',
  'L2 (Vector Search)': 'L2',
  'LLM API': 'LLM'
};

export function RecentSales({ entries }: { entries: HistoryEntry[] }) {
  const recent = entries.slice(0, 8);
  return (
    <Card className='h-full'>
      <CardHeader>
        <CardTitle>Recent Queries</CardTitle>
        <CardDescription>Last {recent.length} queries through Cache-Craft</CardDescription>
      </CardHeader>
      <CardContent>
        <div className='space-y-4'>
          {recent.map((entry, i) => (
            <div key={i} className='flex items-start gap-3'>
              <Badge
                variant='outline'
                className={`mt-0.5 shrink-0 text-[10px] font-semibold ${STATUS_STYLES[entry.result_type] ?? ''}`}
              >
                {TIER_SHORT[entry.source] ?? entry.result_type === 'CACHE_HIT' ? 'HIT' : 'MISS'}
              </Badge>
              <div className='min-w-0 flex-1'>
                <p className='truncate text-sm font-medium leading-none'>{entry.query_text}</p>
                <p className='text-muted-foreground mt-1 text-xs'>
                  {entry.latency_ms.toFixed(1)}ms
                  {entry.similarity_score > 0 && ` · ${(entry.similarity_score * 100).toFixed(0)}% sim`}
                </p>
              </div>
            </div>
          ))}
          {recent.length === 0 && (
            <p className='text-muted-foreground text-sm'>No queries yet. Try the Playground!</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
