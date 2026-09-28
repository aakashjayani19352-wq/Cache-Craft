'use client';

import { LabelList, Pie, PieChart, Cell, Legend } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent
} from '@/components/ui/chart';
import { TierBreakdown } from '@/lib/api';

const TIER_COLORS: Record<string, string> = {
  'L0 (Memory LRU)': 'var(--chart-1)',
  'L0 (In-Memory LRU Cache)': 'var(--chart-1)',
  'L1 (Hash Lookup)': 'var(--chart-2)',
  'L1 (Hash Lookup - Database)': 'var(--chart-2)',
  'L2 (Vector Search - Database)': 'var(--chart-3)',
  'L2 (Vector Search)': 'var(--chart-3)',
  'LLM API': 'var(--chart-4)'
};

const TIER_LABELS: Record<string, string> = {
  'L0 (Memory LRU)': 'L0 Memory',
  'L0 (In-Memory LRU Cache)': 'L0 Memory',
  'L1 (Hash Lookup)': 'L1 Hash',
  'L1 (Hash Lookup - Database)': 'L1 Hash',
  'L2 (Vector Search - Database)': 'L2 Vector',
  'L2 (Vector Search)': 'L2 Vector',
  'LLM API': 'LLM Miss'
};

export function PieGraph({ data }: { data: TierBreakdown }) {
  const chartData = Object.entries(data).map(([tier, stats]) => ({
    name: TIER_LABELS[tier] ?? tier,
    value: stats.count,
    fill: TIER_COLORS[tier] ?? 'var(--chart-5)'
  }));

  const chartConfig = Object.fromEntries(
    chartData.map((d) => [d.name, { label: d.name, color: d.fill }])
  ) as ChartConfig;

  return (
    <Card className='flex h-full flex-col'>
      <CardHeader className='items-center pb-0'>
        <CardTitle>Cache Tier Distribution</CardTitle>
        <CardDescription>Queries served by each cache tier</CardDescription>
      </CardHeader>
      <CardContent className='flex flex-1 items-center justify-center pb-0'>
        <ChartContainer
          config={chartConfig}
          className='[&_.recharts-text]:fill-background mx-auto aspect-square max-h-[300px] min-h-[250px]'
        >
          <PieChart>
            <ChartTooltip content={<ChartTooltipContent nameKey='name' />} />
            <Pie
              data={chartData}
              innerRadius={40}
              dataKey='value'
              cornerRadius={6}
              paddingAngle={3}
            >
              {chartData.map((entry, i) => (
                <Cell key={i} fill={entry.fill} />
              ))}
              <LabelList
                dataKey='value'
                stroke='none'
                fontSize={12}
                fontWeight={600}
                fill='currentColor'
                formatter={(v: number) => (v > 0 ? String(v) : '')}
              />
            </Pie>
          </PieChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
