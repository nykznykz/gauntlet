'use client';

import { Trophy, TrendingUp, TrendingDown } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { leaderboardApi } from '@/lib/api';
import { useAppStore } from '@/lib/store';
import { LeaderboardEntry } from '@/types';

export function LeaderboardTable() {
  const selectedCompetitionId = useAppStore((state) => state.selectedCompetitionId);

  // Fetch leaderboard data
  const { data: entries, isLoading: loading, error } = useQuery({
    queryKey: ['leaderboard', selectedCompetitionId],
    queryFn: async () => {
      if (!selectedCompetitionId) return null;
      const response = await leaderboardApi.get(selectedCompetitionId);
      return response.data;
    },
    enabled: !!selectedCompetitionId,
    refetchInterval: 10000,
  });

  if (loading) {
    return <div className="text-center py-8 text-gray-500">Loading leaderboard...</div>;
  }

  if (error) {
    return <div className="text-center py-8 text-red-500">Error loading leaderboard</div>;
  }

  if (!entries || entries.length === 0) {
    return <div className="text-center py-8 text-gray-500">No participants yet</div>;
  }

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Trophy className="w-5 h-5 text-yellow-500" />;
    if (rank === 2) return <Trophy className="w-5 h-5 text-gray-400" />;
    if (rank === 3) return <Trophy className="w-5 h-5 text-amber-600" />;
    return <span className="w-5 h-5 flex items-center justify-center text-sm font-semibold text-gray-500">{rank}</span>;
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="border-b-2 border-gray-200 dark:border-zinc-800">
          <tr className="text-left text-gray-600 dark:text-gray-400">
            <th className="pb-3 font-semibold">Rank</th>
            <th className="pb-3 font-semibold">Participant</th>
            <th className="pb-3 font-semibold text-right">Equity</th>
            <th className="pb-3 font-semibold text-right">PnL</th>
            <th className="pb-3 font-semibold text-right">Return %</th>
            <th className="pb-3 font-semibold text-right">Win Rate</th>
            <th className="pb-3 font-semibold text-right">Trades</th>
            <th className="pb-3 font-semibold">Status</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <tr
              key={entry.participant_id}
              className={`border-b border-gray-100 dark:border-zinc-800 last:border-0 ${
                entry.status === 'liquidated' ? 'opacity-50' : ''
              }`}
            >
              <td className="py-4">
                <div className="flex items-center">
                  {getRankIcon(entry.rank)}
                </div>
              </td>
              <td className="py-4">
                <div className="font-semibold">{entry.name}</div>
              </td>
              <td className="py-4 text-right font-mono">
                ${Number(entry.equity).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </td>
              <td className={`py-4 text-right font-mono font-semibold ${
                Number(entry.total_pnl) >= 0 ? 'text-profit' : 'text-loss'
              }`}>
                {Number(entry.total_pnl) >= 0 ? '+' : ''}${Math.abs(Number(entry.total_pnl)).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </td>
              <td className={`py-4 text-right font-mono font-semibold ${
                Number(entry.total_pnl_pct) >= 0 ? 'text-profit' : 'text-loss'
              }`}>
                <div className="flex items-center justify-end">
                  {Number(entry.total_pnl_pct) >= 0 ? (
                    <TrendingUp className="w-4 h-4 mr-1" />
                  ) : (
                    <TrendingDown className="w-4 h-4 mr-1" />
                  )}
                  {Number(entry.total_pnl_pct) >= 0 ? '+' : ''}{Number(entry.total_pnl_pct).toFixed(2)}%
                </div>
              </td>
              <td className="py-4 text-right font-mono">{Number(entry.win_rate).toFixed(1)}%</td>
              <td className="py-4 text-right font-mono">{entry.total_trades}</td>
              <td className="py-4">
                <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                  entry.status === 'active'
                    ? 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400'
                    : 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400'
                }`}>
                  {entry.status.toUpperCase()}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
