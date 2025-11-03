"""Technical indicators calculation service"""
import pandas as pd
import pandas_ta as ta
from typing import Dict, List, Any, Optional
from decimal import Decimal


class TechnicalIndicatorService:
    """Service for calculating technical indicators from OHLCV data"""

    def calculate_indicators(self, ohlcv_data: List[Dict[str, Any]]) -> Dict[str, List[float]]:
        """
        Calculate technical indicators from OHLCV data

        Args:
            ohlcv_data: List of OHLCV candles with keys: timestamp, open, high, low, close, volume

        Returns:
            Dictionary with indicator series (oldest → newest)
        """
        if not ohlcv_data or len(ohlcv_data) < 20:
            # Need at least 20 candles for EMA(20)
            return self._empty_indicators()

        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'timestamp': candle['timestamp'],
                'open': float(candle['open']) if isinstance(candle['open'], Decimal) else candle['open'],
                'high': float(candle['high']) if isinstance(candle['high'], Decimal) else candle['high'],
                'low': float(candle['low']) if isinstance(candle['low'], Decimal) else candle['low'],
                'close': float(candle['close']) if isinstance(candle['close'], Decimal) else candle['close'],
                'volume': float(candle['volume']) if isinstance(candle['volume'], Decimal) else candle['volume'],
            }
            for candle in ohlcv_data
        ])

        # Calculate indicators using pandas-ta
        indicators = {}

        # EMA (20-period)
        df['ema_20'] = ta.ema(df['close'], length=20)
        indicators['ema_20'] = df['ema_20'].bfill().tolist()

        # RSI (7-period and 14-period)
        df['rsi_7'] = ta.rsi(df['close'], length=7)
        df['rsi_14'] = ta.rsi(df['close'], length=14)
        indicators['rsi_7'] = df['rsi_7'].bfill().tolist()
        indicators['rsi_14'] = df['rsi_14'].bfill().tolist()

        # MACD (standard 12, 26, 9)
        macd_result = ta.macd(df['close'], fast=12, slow=26, signal=9)
        if macd_result is not None:
            df['macd'] = macd_result['MACD_12_26_9']
            df['macd_signal'] = macd_result['MACDs_12_26_9']
            df['macd_histogram'] = macd_result['MACDh_12_26_9']

            indicators['macd'] = df['macd'].bfill().tolist()
            indicators['macd_signal'] = df['macd_signal'].bfill().tolist()
            indicators['macd_histogram'] = df['macd_histogram'].bfill().tolist()
        else:
            indicators['macd'] = [0.0] * len(df)
            indicators['macd_signal'] = [0.0] * len(df)
            indicators['macd_histogram'] = [0.0] * len(df)

        return indicators

    def _empty_indicators(self) -> Dict[str, List[float]]:
        """Return empty indicators structure"""
        return {
            'ema_20': [],
            'rsi_7': [],
            'rsi_14': [],
            'macd': [],
            'macd_signal': [],
            'macd_histogram': [],
        }

    def format_market_data_with_indicators(
        self,
        symbol: str,
        ohlcv_data: List[Dict[str, Any]],
        current_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Format market data with technical indicators for LLM prompt

        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            ohlcv_data: List of OHLCV candles (oldest → newest)
            current_price: Current market price (optional, will use last close if not provided)

        Returns:
            Formatted market data dictionary
        """
        indicators = self.calculate_indicators(ohlcv_data)

        # Extract price and volume history - only last 5 candles for compactness
        recent_candles = ohlcv_data[-5:] if len(ohlcv_data) > 5 else ohlcv_data

        price_history = [
            {
                'timestamp': candle['timestamp'],
                'open': float(candle['open']) if isinstance(candle['open'], Decimal) else candle['open'],
                'high': float(candle['high']) if isinstance(candle['high'], Decimal) else candle['high'],
                'low': float(candle['low']) if isinstance(candle['low'], Decimal) else candle['low'],
                'close': float(candle['close']) if isinstance(candle['close'], Decimal) else candle['close'],
                'volume': float(candle['volume']) if isinstance(candle['volume'], Decimal) else candle['volume'],
            }
            for candle in recent_candles
        ]

        # Use last close price if current_price not provided
        last_price = current_price if current_price is not None else (
            price_history[-1]['close'] if price_history else None
        )

        # Compact indicators: only include latest value (current state)
        compact_indicators = {}
        for key in ['ema_20', 'rsi_7', 'rsi_14', 'macd', 'macd_signal', 'macd_histogram']:
            values = indicators.get(key, [])
            if values and len(values) > 0:
                # Get the last non-zero/non-null value
                latest = values[-1] if values[-1] is not None else None
                compact_indicators[key] = latest
            else:
                compact_indicators[key] = None

        return {
            'symbol': symbol,
            'current_price': last_price,
            'price_history': price_history,  # Last 5 candles only
            'technical_indicators': compact_indicators  # Just the latest value of each indicator
        }


# Global instance
technical_indicator_service = TechnicalIndicatorService()
