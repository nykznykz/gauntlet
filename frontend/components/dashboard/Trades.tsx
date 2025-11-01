'use client';

import { useQuery } from '@tanstack/react-query';
import { tradeApi } from '@/lib/api';
import { useAppStore } from '@/lib/store';
import { Trade } from '@/types';
import { format } from 'date-fns';
import { TrendingUp, TrendingDown } from 'lucide-react';

export function Trades() {
  const selectedParticipantId = useAppStore((state) => state.selectedParticipantId);

  // Fetch trades data
  const { data: trades, isLoading, error } = useQuery({
    queryKey: ['trades', selectedParticipantId],
    queryFn: async () => {
      if (!selectedParticipantId) return null;
      const response = await tradeApi.list(selectedParticipantId, 20);
      return response.data;
    },
    enabled: !!selectedParticipantId,
    refetchInterval: 5000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-gray-500">Loading trades...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-red-500">Error loading trades</div>
      </div>
    );
  }

  if (!trades || trades.length === 0) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-gray-500">No trades yet</div>
      </div>
    );
  }

  const formatTime = (timestamp: string) => {
    try {
      return format(new Date(timestamp), 'MM/dd HH:mm');
    } catch {
      return timestamp;
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 dark:border-zinc-800">
            <th className="text-left py-3 px-2 font-medium text-gray-600 dark:text-gray-400">Time</th>
            <th className="text-left py-3 px-2 font-medium text-gray-600 dark:text-gray-400">Symbol</th>
            <th className="text-left py-3 px-2 font-medium text-gray-600 dark:text-gray-400">Action</th>
            <th className="text-right py-3 px-2 font-medium text-gray-600 dark:text-gray-400">Qty</th>
            <th className="text-right py-3 px-2 font-medium text-gray-600 dark:text-gray-400">Price</th>
            <th className="text-right py-3 px-2 font-medium text-gray-600 dark:text-gray-400">P&L</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade) => {
            const pnl = trade.pnl || 0;
            const pnlColor = pnl >= 0 ? 'text-green-600' : 'text-red-600';
            const sideColor = trade.side === 'long' ? 'text-green-600' : 'text-red-600';
            const actionLabel = `${trade.action} ${trade.side}`.toUpperCase();

            return (
              <tr
                key={trade.id}
                className="border-b border-gray-100 dark:border-zinc-800 hover:bg-gray-50 dark:hover:bg-zinc-800/50"
              >
                <td className="py-3 px-2 text-gray-600 dark:text-gray-400">
                  {formatTime(trade.timestamp)}
                </td>
                <td className="py-3 px-2 font-medium">{trade.symbol}</td>
                <td className="py-3 px-2">
                  <span className={`flex items-center gap-1 ${sideColor} font-medium`}>
                    {trade.side === 'long' ? (
                      <TrendingUp className="w-3 h-3" />
                    ) : (
                      <TrendingDown className="w-3 h-3" />
                    )}
                    {actionLabel}
                  </span>
                </td>
                <td className="py-3 px-2 text-right">{trade.quantity.toLocaleString()}</td>
                <td className="py-3 px-2 text-right">${trade.price.toLocaleString()}</td>
                <td className={`py-3 px-2 text-right font-medium ${pnlColor}`}>
                  {trade.action === 'close' && pnl !== 0 ? `$${pnl.toLocaleString()}` : '-'}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
