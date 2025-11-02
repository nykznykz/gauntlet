'use client';

import { useQuery } from '@tanstack/react-query';
import { marketDataApi } from '@/lib/api';
import { TickerPrice } from '@/types';

export function PriceTicker() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['marketTickers'],
    queryFn: async () => {
      const response = await marketDataApi.tickers('BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT');
      console.log('Ticker API response:', response);
      return response.data?.tickers || [];
    },
    refetchInterval: 10000, // Refetch every 10 seconds
    retry: 3,
  });

  if (error) {
    console.error('Price ticker error:', error);
  }

  if (isLoading || !data || data.length === 0) {
    return null;
  }

  const formatSymbol = (symbol: string) => {
    // Convert BTCUSDT to BTC/USD format
    if (symbol.endsWith('USDT')) {
      return symbol.replace('USDT', '/USD');
    }
    return symbol;
  };

  const formatPrice = (price: number) => {
    return price.toFixed(2);
  };

  const formatChange = (change: number) => {
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(2)}%`;
  };

  return (
    <div className="bg-zinc-950 border-b border-zinc-800 overflow-hidden">
      <div className="relative h-10 flex items-center">
        {/* Animated ticker */}
        <div className="animate-ticker flex items-center gap-8 whitespace-nowrap">
          {/* Duplicate items for seamless loop */}
          {[...data, ...data].map((ticker: any, index: number) => (
            <div key={`ticker-${index}`} className="flex items-center gap-2 text-sm">
              <span className="text-gray-400 font-medium">
                {formatSymbol(ticker.symbol)}
              </span>
              <span className="text-white font-semibold">
                ${formatPrice(ticker.price)}
              </span>
              <span
                className={`font-medium ${
                  ticker.change_percent_24h >= 0 ? 'text-green-500' : 'text-red-500'
                }`}
              >
                {formatChange(ticker.change_percent_24h)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
