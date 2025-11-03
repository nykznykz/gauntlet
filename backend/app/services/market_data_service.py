"""Market data service"""
from decimal import Decimal
from typing import Dict, List, Optional, Any
from app.market.binance import binance_provider
from app.services.technical_indicators import technical_indicator_service


class MarketDataService:
    """Service for fetching market data"""

    def __init__(self):
        self.binance = binance_provider

    def get_price(self, symbol: str, asset_class: str = "crypto") -> Optional[Decimal]:
        """Get current price for a symbol"""
        if asset_class == "crypto":
            return self.binance.get_current_price(symbol)
        else:
            # TODO: Add other providers (yfinance, etc.)
            raise NotImplementedError(f"Asset class {asset_class} not yet supported")

    def get_multiple_prices(self, symbols: List[str], asset_class: str = "crypto") -> Dict[str, Decimal]:
        """Get prices for multiple symbols"""
        if asset_class == "crypto":
            return self.binance.get_multiple_prices(symbols)
        else:
            raise NotImplementedError(f"Asset class {asset_class} not yet supported")

    def get_ticker_data(self, symbol: str, asset_class: str = "crypto") -> Optional[dict]:
        """Get full ticker data"""
        if asset_class == "crypto":
            return self.binance.get_ticker_data(symbol)
        else:
            raise NotImplementedError(f"Asset class {asset_class} not yet supported")

    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 100,
        asset_class: str = "crypto"
    ) -> list:
        """Get OHLCV candlestick data"""
        if asset_class == "crypto":
            return self.binance.get_ohlcv(symbol, timeframe, limit)
        else:
            raise NotImplementedError(f"Asset class {asset_class} not yet supported")

    def get_enhanced_market_data(
        self,
        symbols: List[str],
        asset_class: str = "crypto",
        timeframe: str = "3m",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get enhanced market data with multi-timeframe price history and technical indicators

        Provides data across multiple timeframes for better context:
        - 1m: Very short-term (last 10 minutes)
        - 5m: Short-term (last 50 minutes)
        - 15m: Medium-term (last 2.5 hours)
        - 1h: Longer-term (last 10 hours)

        Args:
            symbols: List of trading symbols
            asset_class: Asset class (default: "crypto")
            timeframe: Ignored - uses multiple timeframes
            limit: Ignored - uses fixed limits per timeframe

        Returns:
            List of market data dictionaries for each symbol with multi-timeframe data
        """
        if asset_class != "crypto":
            raise NotImplementedError(f"Asset class {asset_class} not yet supported")

        enhanced_data = []

        # Define timeframes with their limits
        # Fetch enough data for indicators (50 candles for MACD) but only show last 5 in price_history
        timeframes = [
            ("1m", 50),   # Fetch 50, show last 5 (~5 minutes shown)
            ("5m", 50),   # Fetch 50, show last 5 (~25 minutes shown)
            ("15m", 50),  # Fetch 50, show last 5 (~1.25 hours shown)
            ("1h", 50),   # Fetch 50, show last 5 (~5 hours shown)
        ]

        for symbol in symbols:
            # Fetch current price
            current_price = self.binance.get_current_price(symbol)
            current_price_float = float(current_price) if current_price else None

            # Fetch data for each timeframe
            timeframe_data = {}
            for tf, tf_limit in timeframes:
                ohlcv_data = self.binance.get_ohlcv(symbol, tf, tf_limit)

                # Calculate technical indicators for this timeframe
                tf_formatted = technical_indicator_service.format_market_data_with_indicators(
                    symbol=symbol,
                    ohlcv_data=ohlcv_data,
                    current_price=current_price_float
                )

                # Store under timeframe key
                timeframe_data[tf] = {
                    'price_history': tf_formatted['price_history'],
                    'technical_indicators': tf_formatted['technical_indicators']
                }

            # Combine into single market data structure
            market_data = {
                'symbol': symbol,
                'current_price': current_price_float,
                'timeframes': timeframe_data  # Multi-timeframe data
            }

            enhanced_data.append(market_data)

        return enhanced_data


# Global instance
market_data_service = MarketDataService()
