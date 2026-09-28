'use client';

import { Bar, BarChart, XAxis, YAxis } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent
} from '@/components/ui/chart';

interface LatencyData {
  hit: { p50: number; p90: number; p99: number };
  miss: { p50: number; p90: number; p99: number };
}

const chartConfig = {
  hit: { label: 'Cache Hit (ms)', color: 'var(--chart-1)' },
  miss: { label: 'LLM Miss (ms)', color: 'var(--chart-4)' }
} satisfies ChartConfig;

export function BarGraph({ data }: { data: LatencyData }) {
  const chartData = [
    { percentile: 'p50', hit: data.hit.p50, miss: data.miss.p50 },
    { percentile: 'p90', hit: data.hit.p90, miss: data.miss.p90 },
    { percentile: 'p99', hit: data.hit.p99, miss: data.miss.p99 }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Latency Percentiles</CardTitle>
        <CardDescription>Cache hit vs LLM miss response times (ms)</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <BarChart accessibilityLayer data={chartData} barCategoryGap='30%'>
            <XAxis dataKey='percentile' tickLine={false} axisLine={false} tickMargin={8} />
            <YAxis tickLine={false} axisLine={false} tickMargin={8} unit='ms' />
            <ChartTooltip cursor={false} content={<ChartTooltipContent indicator='dashed' />} />
            <Bar dataKey='hit' fill='var(--color-hit)' radius={4} />
            <Bar dataKey='miss' fill='var(--color-miss)' radius={4} />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
