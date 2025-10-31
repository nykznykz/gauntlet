'use client';

import { useQuery } from '@tanstack/react-query';
import { participantApi, portfolioApi } from '@/lib/api';
import { useAppStore } from '@/lib/store';
import { Participant, Portfolio } from '@/types';
import { TrendingUp, TrendingDown, DollarSign, Activity, Target, Percent } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon: React.ReactNode;
}

function StatCard({ title, value, change, changeType = 'neutral', icon }: StatCardProps) {
  const changeColor =
    changeType === 'positive'
      ? 'text-green-600'
      : changeType === 'negative'
      ? 'text-red-600'
      : 'text-gray-600';

  return (
    <div className="bg-white dark:bg-zinc-900 rounded-lg shadow-sm border border-gray-200 dark:border-zinc-800 p-6">
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
        <div className="text-gray-400">{icon}</div>
      </div>
      <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
      {change && (
        <p className={`text-sm mt-1 flex items-center gap-1 ${changeColor}`}>
          {changeType === 'positive' && <TrendingUp className="w-4 h-4" />}
          {changeType === 'negative' && <TrendingDown className="w-4 h-4" />}
          {change}
        </p>
      )}
    </div>
  );
}

export function CompetitionStats() {
  const selectedParticipantId = useAppStore((state) => state.selectedParticipantId);

  // Fetch participant data
  const { data: participantData } = useQuery({
    queryKey: ['participant', selectedParticipantId],
    queryFn: async () => {
      if (!selectedParticipantId) return null;
      const response = await participantApi.get(selectedParticipantId);
      return response.data as Participant;
    },
    enabled: !!selectedParticipantId,
    refetchInterval: 5000,
  });

  // Fetch portfolio data
  const { data: portfolioData } = useQuery({
    queryKey: ['portfolio', selectedParticipantId],
    queryFn: async () => {
      if (!selectedParticipantId) return null;
      const response = await portfolioApi.get(selectedParticipantId);
      return response.data as Portfolio;
    },
    enabled: !!selectedParticipantId,
    refetchInterval: 5000,
  });

  if (!participantData || !portfolioData) {
    return (
      <>
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="bg-white dark:bg-zinc-900 rounded-lg shadow-sm border border-gray-200 dark:border-zinc-800 p-6 animate-pulse"
          >
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
          </div>
        ))}
      </>
    );
  }

  const totalPnl = portfolioData.total_pnl || 0;
  const totalPnlPct =
    participantData.initial_capital > 0
      ? ((totalPnl / participantData.initial_capital) * 100).toFixed(2)
      : '0.00';

  const winRate =
    participantData.total_trades > 0
      ? ((participantData.winning_trades / participantData.total_trades) * 100).toFixed(1)
      : '0.0';

  return (
    <>
      <StatCard
        title="Current Equity"
        value={`$${portfolioData.equity.toLocaleString()}`}
        change={`${totalPnlPct}%`}
        changeType={totalPnl >= 0 ? 'positive' : 'negative'}
        icon={<DollarSign className="w-5 h-5" />}
      />

      <StatCard
        title="Total P&L"
        value={`$${totalPnl.toLocaleString()}`}
        changeType={totalPnl >= 0 ? 'positive' : 'negative'}
        icon={totalPnl >= 0 ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
      />

      <StatCard
        title="Total Trades"
        value={participantData.total_trades.toString()}
        change={`${participantData.winning_trades}W / ${participantData.losing_trades}L`}
        changeType="neutral"
        icon={<Activity className="w-5 h-5" />}
      />

      <StatCard
        title="Win Rate"
        value={`${winRate}%`}
        changeType={parseFloat(winRate) >= 50 ? 'positive' : 'negative'}
        icon={<Target className="w-5 h-5" />}
      />
    </>
  );
}
