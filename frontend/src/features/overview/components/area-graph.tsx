'use client';

import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent
} from '@/components/ui/chart';
import { Badge } from '@/components/ui/badge';
import { Icons } from '@/components/icons';

interface HourlyStat {
  hour: string;
  total: number;
  hits: number;
}

const chartConfig = {
  hits: { label: 'Cache Hits', color: 'var(--chart-1)' },
  total: { label: 'Total Queries', color: 'var(--chart-2)' }
} satisfies ChartConfig;

export function AreaGraph({ data }: { data: HourlyStat[] }) {
  const formatted = data.map((d) => ({
    hour: new Date(d.hour).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    hits: d.hits,
    total: d.total
  }));

  const lastHit = formatted.at(-1)?.hits ?? 0;
  const prevHit = formatted.at(-2)?.hits ?? 0;
  const trend = prevHit > 0 ? Math.round(((lastHit - prevHit) / prevHit) * 100) : 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle className='flex items-center gap-2'>
          Query Traffic
          <Badge variant='outline'>
            {trend >= 0 ? <Icons.trendingUp /> : <Icons.trendingDown />}
            {trend >= 0 ? '+' : ''}{trend}%
          </Badge>
        </CardTitle>
        <CardDescription>Cache hits vs total queries per hour</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <AreaChart accessibilityLayer data={formatted}>
            <CartesianGrid vertical={false} strokeDasharray='3 3' />
            <XAxis dataKey='hour' tickLine={false} axisLine={false} tickMargin={8} />
            <YAxis tickLine={false} axisLine={false} tickMargin={8} />
            <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
            <defs>
              <linearGradient id='fillHits' x1='0' y1='0' x2='0' y2='1'>
                <stop offset='5%' stopColor='var(--chart-1)' stopOpacity={0.8} />
                <stop offset='95%' stopColor='var(--chart-1)' stopOpacity={0.1} />
              </linearGradient>
              <linearGradient id='fillTotal' x1='0' y1='0' x2='0' y2='1'>
                <stop offset='5%' stopColor='var(--chart-2)' stopOpacity={0.4} />
                <stop offset='95%' stopColor='var(--chart-2)' stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <Area
              dataKey='total'
              type='monotone'
              fill='url(#fillTotal)'
              stroke='var(--color-total)'
              strokeWidth={1.5}
            />
            <Area
              dataKey='hits'
              type='monotone'
              fill='url(#fillHits)'
              stroke='var(--color-hits)'
              strokeWidth={2}
            />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
