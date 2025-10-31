"""Binance market data provider"""
import ccxt
from decimal import Decimal
from typing import Optional, Dict, Any
from app.config import settings
from app.utils.cache import cache


class BinanceProvider:
    """Binance market data provider using CCXT"""

    def __init__(self):
        # Use public endpoints by default (no API key needed)
        # Only add API keys if they're actually provided
        exchange_config = {
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',  # Use spot market
            }
        }

        # Only add API keys if they exist and are not empty
        if settings.BINANCE_API_KEY and settings.BINANCE_API_SECRET:
            exchange_config['apiKey'] = settings.BINANCE_API_KEY
            exchange_config['secret'] = settings.BINANCE_API_SECRET
            print("✅ Binance: Using authenticated API (with API keys)")
        else:
            print("✅ Binance: Using public API (no API keys needed)")

        self.exchange = ccxt.binance(exchange_config)

    def get_current_price(self, symbol: str) -> Optional[Decimal]:
        """Get current price for a symbol"""
        cache_key = f"price:{symbol}"

        # Check cache first
        cached_price = cache.get(cache_key)
        if cached_price is not None:
            return Decimal(str(cached_price))

        try:
            ticker = self.exchange.fetch_ticker(symbol)
            price = Decimal(str(ticker['last']))

            # Cache for 60 seconds
            cache.set(cache_key, float(price), ttl=settings.PRICE_CACHE_TTL)

            return price
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None

    def get_ticker_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get full ticker data including volume, change, etc."""
        try:
            ticker = self.exchange.fetch_ticker(symbol)

            return {
                "symbol": symbol,
                "price": Decimal(str(ticker['last'])),
                "bid": Decimal(str(ticker['bid'])) if ticker['bid'] else None,
                "ask": Decimal(str(ticker['ask'])) if ticker['ask'] else None,
                "high_24h": Decimal(str(ticker['high'])) if ticker['high'] else None,
                "low_24h": Decimal(str(ticker['low'])) if ticker['low'] else None,
                "volume_24h": Decimal(str(ticker['quoteVolume'])) if ticker.get('quoteVolume') else None,
                "change_24h_pct": Decimal(str(ticker['percentage'])) if ticker.get('percentage') else None,
            }
        except Exception as e:
            print(f"Error fetching ticker for {symbol}: {e}")
            return None

    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: int = 100
    ) -> list:
        """Get OHLCV candlestick data"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

            return [
                {
                    "timestamp": candle[0],
                    "open": Decimal(str(candle[1])),
                    "high": Decimal(str(candle[2])),
                    "low": Decimal(str(candle[3])),
                    "close": Decimal(str(candle[4])),
                    "volume": Decimal(str(candle[5])),
                }
                for candle in ohlcv
            ]
        except Exception as e:
            print(f"Error fetching OHLCV for {symbol}: {e}")
            return []

    def get_multiple_prices(self, symbols: list[str]) -> Dict[str, Decimal]:
        """Get current prices for multiple symbols"""
        prices = {}

        for symbol in symbols:
            price = self.get_current_price(symbol)
            if price is not None:
                prices[symbol] = price

        return prices


# Global instance
binance_provider = BinanceProvider()
