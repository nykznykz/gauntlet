'use client';

import { useEffect, useRef, useState } from 'react';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

export type WebSocketMessage = {
  type: 'portfolio_update' | 'position_update' | 'trade_executed' | 'market_data' | 'price_update';
  data: any;
  timestamp: string;
};

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export function useWebSocket(onMessage?: (message: WebSocketMessage) => void) {
  const [status, setStatus] = useState<WebSocketStatus>('disconnected');
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

  const connect = () => {
    try {
      setStatus('connecting');
      ws.current = new WebSocket(WS_URL);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setStatus('connected');
      };

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setStatus('error');
      };

      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
        setStatus('disconnected');

        // Attempt to reconnect after 5 seconds
        reconnectTimeout.current = setTimeout(() => {
          console.log('Attempting to reconnect...');
          connect();
        }, 5000);
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setStatus('error');
    }
  };

  const disconnect = () => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
    }
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
    setStatus('disconnected');
  };

  const send = (message: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Cannot send message.');
    }
  };

  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, []);

  return { status, send, connect, disconnect };
}

// Hook for subscribing to specific data streams
export function useMarketDataStream(symbols: string[]) {
  const [prices, setPrices] = useState<Record<string, any>>({});

  const handleMessage = (message: WebSocketMessage) => {
    if (message.type === 'price_update' || message.type === 'market_data') {
      setPrices((prev) => ({
        ...prev,
        [message.data.symbol]: message.data,
      }));
    }
  };

  const { status } = useWebSocket(handleMessage);

  return { prices, status };
}

// Hook for portfolio updates
export function usePortfolioStream(participantId: string) {
  const [portfolio, setPortfolio] = useState<any>(null);
  const [positions, setPositions] = useState<any[]>([]);
  const [trades, setTrades] = useState<any[]>([]);

  const handleMessage = (message: WebSocketMessage) => {
    switch (message.type) {
      case 'portfolio_update':
        if (message.data.participant_id === participantId) {
          setPortfolio(message.data);
        }
        break;
      case 'position_update':
        if (message.data.participant_id === participantId) {
          setPositions((prev) => {
            const index = prev.findIndex((p) => p.id === message.data.id);
            if (index >= 0) {
              const updated = [...prev];
              updated[index] = message.data;
              return updated;
            }
            return [...prev, message.data];
          });
        }
        break;
      case 'trade_executed':
        if (message.data.participant_id === participantId) {
          setTrades((prev) => [message.data, ...prev].slice(0, 50));
        }
        break;
    }
  };

  const { status } = useWebSocket(handleMessage);

  return { portfolio, positions, trades, status };
}
