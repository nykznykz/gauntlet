"""Market data service"""
from decimal import Decimal
from typing import Dict, List, Optional
from app.market.binance import binance_provider


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


# Global instance
market_data_service = MarketDataService()
