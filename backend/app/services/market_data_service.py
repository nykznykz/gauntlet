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
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get enhanced market data with price history, volume, and technical indicators

        Similar to nof1.ai approach: provides historical data (oldest → newest) with
        technical indicators (EMA, MACD, RSI) calculated on the fly.

        Args:
            symbols: List of trading symbols
            asset_class: Asset class (default: "crypto")
            timeframe: Candlestick timeframe (default: "3m" for 3-minute intervals)
            limit: Number of historical candles to fetch (default: 100)

        Returns:
            List of market data dictionaries for each symbol with price history and indicators
        """
        if asset_class != "crypto":
            raise NotImplementedError(f"Asset class {asset_class} not yet supported")

        enhanced_data = []

        for symbol in symbols:
            # Fetch current price
            current_price = self.binance.get_current_price(symbol)
            current_price_float = float(current_price) if current_price else None

            # Fetch historical OHLCV data
            ohlcv_data = self.binance.get_ohlcv(symbol, timeframe, limit)

            # Calculate technical indicators and format data
            market_data = technical_indicator_service.format_market_data_with_indicators(
                symbol=symbol,
                ohlcv_data=ohlcv_data,
                current_price=current_price_float
            )

            enhanced_data.append(market_data)

        return enhanced_data


# Global instance
market_data_service = MarketDataService()
