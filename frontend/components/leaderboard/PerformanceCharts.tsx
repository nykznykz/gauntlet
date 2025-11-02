'use client';

import { useQuery } from '@tanstack/react-query';
import { competitionApi } from '@/lib/api';
import { useAppStore } from '@/lib/store';
import { MultiParticipantHistory } from '@/types';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { format } from 'date-fns';
import { getParticipantLogo } from '@/lib/llm-logos';
import Image from 'next/image';

// Color palette for different traders
const TRADER_COLORS = [
  '#3b82f6', // blue
  '#10b981', // green
  '#f59e0b', // amber
  '#ef4444', // red
  '#8b5cf6', // purple
  '#ec4899', // pink
  '#06b6d4', // cyan
  '#84cc16', // lime
];

interface ChartDataPoint {
  timestamp: string;
  [key: string]: number | string;
}

// Custom Legend component with LLM logos
interface CustomLegendProps {
  payload?: Array<{
    value: string;
    color: string;
  }>;
}

const CustomLegend = ({ payload }: CustomLegendProps) => {
  if (!payload) return null;

  return (
    <div className="flex flex-wrap justify-center gap-4 pt-4">
      {payload.map((entry, index) => {
        const logoPath = getParticipantLogo(entry.value);
        return (
          <div key={`legend-${index}`} className="flex items-center gap-2">
            {logoPath ? (
              <Image
                src={logoPath}
                alt={entry.value}
                width={20}
                height={20}
                className="rounded"
              />
            ) : (
              <div
                className="w-5 h-0.5"
                style={{ backgroundColor: entry.color }}
              />
            )}
            <span className="text-sm text-gray-300">{entry.value}</span>
          </div>
        );
      })}
    </div>
  );
};

// Custom dot component with LLM logo
interface CustomDotProps {
  cx?: number;
  cy?: number;
  payload?: any;
  dataKey?: string;
  index?: number;
  chartData?: ChartDataPoint[];
}

const CustomDot = ({ cx, cy, payload, dataKey, index, chartData }: CustomDotProps) => {
  // Only show logo at the last point (rightmost)
  if (!chartData || index !== chartData.length - 1 || !dataKey) return null;

  const logoPath = getParticipantLogo(dataKey as string);
  if (!logoPath || cx === undefined || cy === undefined) return null;

  return (
    <g>
      {/* Background circle */}
      <circle cx={cx} cy={cy} r={16} fill="white" opacity={0.9} />
      {/* Logo image */}
      <image
        href={logoPath}
        x={cx - 12}
        y={cy - 12}
        width={24}
        height={24}
        clipPath="circle(12px at 12px 12px)"
      />
    </g>
  );
};

export function PerformanceCharts() {
  const selectedCompetitionId = useAppStore((state) => state.selectedCompetitionId);

  const { data, isLoading, error } = useQuery({
    queryKey: ['competitionHistory', selectedCompetitionId],
    queryFn: async () => {
      if (!selectedCompetitionId) return null;
      const response = await competitionApi.history(selectedCompetitionId);
      return response.data as MultiParticipantHistory;
    },
    enabled: !!selectedCompetitionId,
    refetchInterval: 30000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading performance data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-500">Error loading performance data</div>
      </div>
    );
  }

  if (!data || !data.participants || data.participants.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">No performance data available</div>
      </div>
    );
  }

  // Transform the data for Recharts with forward-fill for missing values
  // First, collect all unique timestamps and sort them
  const allTimestamps = new Set<string>();
  data.participants.forEach((participant) => {
    participant.history.forEach((point) => {
      allTimestamps.add(point.recorded_at);
    });
  });

  const sortedTimestamps = Array.from(allTimestamps).sort(
    (a, b) => new Date(a).getTime() - new Date(b).getTime()
  );

  // Create a map of participant -> sorted history
  const participantHistoryMap = new Map<string, typeof data.participants[0]['history']>();
  data.participants.forEach((participant) => {
    participantHistoryMap.set(
      participant.participant_name,
      [...participant.history].sort(
        (a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime()
      )
    );
  });

  // Build chart data with forward-fill
  const chartData: ChartDataPoint[] = sortedTimestamps.map((timestamp) => {
    const dataPoint: ChartDataPoint = { timestamp };

    data.participants.forEach((participant) => {
      const history = participantHistoryMap.get(participant.participant_name)!;
      // Find the most recent value at or before this timestamp
      let value: number | null = null;
      for (const point of history) {
        if (new Date(point.recorded_at).getTime() <= new Date(timestamp).getTime()) {
          value = Number(point.equity);
        } else {
          break;
        }
      }
      // Only add the value if we found a data point (don't show 0 before first timestamp)
      if (value !== null) {
        dataPoint[participant.participant_name] = value;
      }
    });

    return dataPoint;
  });

  const initialCapital = data.participants[0]?.history[0]?.equity
    ? Number(data.participants[0].history[0].equity)
    : 10000;

  const formatXAxis = (timestamp: string) => {
    try {
      return format(new Date(timestamp), 'MM/dd HH:mm');
    } catch {
      return timestamp;
    }
  };

  const formatTooltipLabel = (timestamp: string) => {
    try {
      return format(new Date(timestamp), 'MMM dd, yyyy HH:mm:ss');
    } catch {
      return timestamp;
    }
  };

  // Calculate dynamic Y-axis domain for better visibility
  const calculateYAxisDomain = () => {
    const allValues: number[] = [];
    chartData.forEach((point) => {
      data.participants.forEach((participant) => {
        const value = point[participant.participant_name];
        if (typeof value === 'number') {
          allValues.push(value);
        }
      });
    });

    if (allValues.length === 0) return [0, 10000];

    const minValue = Math.min(...allValues);
    const maxValue = Math.max(...allValues);
    const range = maxValue - minValue;

    // If range is very small (< 1% of max), add more padding to zoom in
    const paddingPercent = range < maxValue * 0.01 ? 0.05 : 0.1;
    const padding = Math.max(range * paddingPercent, maxValue * 0.02);

    return [
      Math.max(0, Math.floor(minValue - padding)),
      Math.ceil(maxValue + padding),
    ];
  };

  const yAxisDomain = calculateYAxisDomain();

  return (
    <div className="w-full h-96">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
          <XAxis
            dataKey="timestamp"
            tickFormatter={formatXAxis}
            stroke="#9ca3af"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            stroke="#9ca3af"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => `$${value.toLocaleString()}`}
            domain={yAxisDomain}
          />
          <Tooltip
            labelFormatter={formatTooltipLabel}
            formatter={(value: number) => [`$${value.toLocaleString()}`, '']}
            contentStyle={{
              backgroundColor: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '6px',
              color: '#f3f4f6',
            }}
          />
          <Legend
            content={<CustomLegend />}
            wrapperStyle={{ paddingTop: '20px' }}
          />

          <ReferenceLine
            y={initialCapital}
            stroke="#6b7280"
            strokeDasharray="5 5"
            label={{ value: 'Initial Capital', fill: '#9ca3af', fontSize: 12 }}
          />

          {data.participants.map((participant, index) => (
            <Line
              key={participant.participant_id}
              type="monotone"
              dataKey={participant.participant_name}
              stroke={TRADER_COLORS[index % TRADER_COLORS.length]}
              strokeWidth={2}
              dot={(props) => {
                const { key, ...restProps } = props;
                return <CustomDot key={key} {...restProps} chartData={chartData} />;
              }}
              activeDot={{ r: 4 }}
              name={participant.participant_name}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
