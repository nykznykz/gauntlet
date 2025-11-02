"""Market data API endpoints"""
from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.market_data_service import market_data_service

router = APIRouter(prefix="/market-data", tags=["market-data"])


class TickerPrice(BaseModel):
    """Ticker price response"""
    symbol: str
    price: float
    change_24h: float
    change_percent_24h: float


class TickerPricesResponse(BaseModel):
    """Multiple ticker prices response"""
    tickers: List[TickerPrice]


@router.get("/tickers", response_model=TickerPricesResponse)
async def get_ticker_prices(symbols: str = "BTCUSDT,ETHUSDT,SOLUSDT,EURUSDT"):
    """
    Get current ticker prices for multiple symbols

    Args:
        symbols: Comma-separated list of symbols (default: BTC, ETH, SOL, EUR)

    Returns:
        TickerPricesResponse with current prices and 24h changes
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        tickers = []

        for symbol in symbol_list:
            ticker_data = market_data_service.get_ticker_data(symbol)

            if ticker_data:
                tickers.append(TickerPrice(
                    symbol=symbol,
                    price=float(ticker_data.get("lastPrice", 0)),
                    change_24h=float(ticker_data.get("priceChange", 0)),
                    change_percent_24h=float(ticker_data.get("priceChangePercent", 0)),
                ))

        return TickerPricesResponse(tickers=tickers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ticker data: {str(e)}")


@router.get("/{symbol}/ticker", response_model=TickerPrice)
async def get_single_ticker(symbol: str):
    """
    Get current ticker price for a single symbol

    Args:
        symbol: Trading symbol (e.g., BTCUSDT)

    Returns:
        TickerPrice with current price and 24h changes
    """
    try:
        ticker_data = market_data_service.get_ticker_data(symbol.upper())

        if not ticker_data:
            raise HTTPException(status_code=404, detail=f"Ticker data not found for {symbol}")

        return TickerPrice(
            symbol=symbol.upper(),
            price=float(ticker_data.get("lastPrice", 0)),
            change_24h=float(ticker_data.get("priceChange", 0)),
            change_percent_24h=float(ticker_data.get("priceChangePercent", 0)),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ticker data: {str(e)}")
