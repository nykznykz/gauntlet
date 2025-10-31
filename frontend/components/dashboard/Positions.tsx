'use client';

import { useQuery } from '@tanstack/react-query';
import { positionApi } from '@/lib/api';
import { useAppStore } from '@/lib/store';
import { Position } from '@/types';
import { TrendingUp, TrendingDown } from 'lucide-react';

export function Positions() {
  const selectedParticipantId = useAppStore((state) => state.selectedParticipantId);

  // Fetch positions data
  const { data, isLoading, error } = useQuery({
    queryKey: ['positions', selectedParticipantId],
    queryFn: async () => {
      if (!selectedParticipantId) return null;
      const response = await positionApi.list(selectedParticipantId);
      return response.data as { positions: Position[] };
    },
    enabled: !!selectedParticipantId,
    refetchInterval: 5000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-gray-500">Loading positions...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-red-500">Error loading positions</div>
      </div>
    );
  }

  if (!data || !data.positions || data.positions.length === 0) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-gray-500">No open positions</div>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 dark:border-zinc-800">
            <th className="text-left py-3 px-2 font-medium text-gray-600 dark:text-gray-400">Symbol</th>
            <th className="text-left py-3 px-2 font-medium text-gray-600 dark:text-gray-400">Side</th>
            <th className="text-right py-3 px-2 font-medium text-gray-600 dark:text-gray-400">Qty</th>
            <th className="text-right py-3 px-2 font-medium text-gray-600 dark:text-gray-400">Entry</th>
            <th className="text-right py-3 px-2 font-medium text-gray-600 dark:text-gray-400">Current</th>
            <th className="text-right py-3 px-2 font-medium text-gray-600 dark:text-gray-400">P&L</th>
            <th className="text-right py-3 px-2 font-medium text-gray-600 dark:text-gray-400">Leverage</th>
          </tr>
        </thead>
        <tbody>
          {data.positions.map((position) => {
            const pnl = position.unrealized_pnl;
            const pnlColor = pnl >= 0 ? 'text-green-600' : 'text-red-600';
            const sideColor = position.side === 'long' ? 'text-green-600' : 'text-red-600';

            return (
              <tr
                key={position.id}
                className="border-b border-gray-100 dark:border-zinc-800 hover:bg-gray-50 dark:hover:bg-zinc-800/50"
              >
                <td className="py-3 px-2 font-medium">{position.symbol}</td>
                <td className="py-3 px-2">
                  <span className={`flex items-center gap-1 ${sideColor} font-medium`}>
                    {position.side === 'long' ? (
                      <TrendingUp className="w-4 h-4" />
                    ) : (
                      <TrendingDown className="w-4 h-4" />
                    )}
                    {position.side.toUpperCase()}
                  </span>
                </td>
                <td className="py-3 px-2 text-right">{position.quantity.toLocaleString()}</td>
                <td className="py-3 px-2 text-right">${position.entry_price.toLocaleString()}</td>
                <td className="py-3 px-2 text-right">${position.current_price.toLocaleString()}</td>
                <td className={`py-3 px-2 text-right font-medium ${pnlColor}`}>
                  ${pnl.toLocaleString()}
                </td>
                <td className="py-3 px-2 text-right">{position.leverage}x</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
