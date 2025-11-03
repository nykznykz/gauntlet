"""LLM prompt builder"""
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple
from app.models.competition import Competition
from app.models.participant import Participant
from app.models.portfolio import Portfolio
from app.models.position import Position


class PromptBuilder:
    """Builder for LLM trading prompts"""

    def build_trading_prompt(
        self,
        competition: Competition,
        participant: Participant,
        portfolio: Portfolio,
        positions: List[Position],
        market_data: Dict[str, Any],
        leaderboard: List[Dict[str, Any]]
    ) -> Tuple[str, str]:
        """
        Build complete trading prompt with context

        Returns:
            Tuple[str, str]: (system_prompt, user_prompt)
        """

        # System prompt contains static instructions and rules
        system_prompt = self._build_system_prompt()

        # User prompt contains dynamic data
        user_prompt_data = {
            "competition_context": self._build_competition_context(competition, participant),
            "portfolio": self._build_portfolio_context(portfolio, positions),
            "market_data": market_data,
            "trading_rules": self._build_trading_rules(competition, portfolio),
            "leaderboard": leaderboard,
        }

        # Convert to formatted JSON
        user_prompt = json.dumps(user_prompt_data, indent=2, default=str)

        return system_prompt, user_prompt

    def _build_competition_context(
        self,
        competition: Competition,
        participant: Participant
    ) -> Dict[str, Any]:
        """Build competition context section"""

        time_remaining = competition.end_time - datetime.now(competition.end_time.tzinfo)

        return {
            "competition_id": str(competition.id),
            "competition_name": competition.name,
            "current_time": datetime.now().isoformat(),
            "time_remaining": str(time_remaining),
        }

    def _build_portfolio_context(
        self,
        portfolio: Portfolio,
        positions: List[Position]
    ) -> Dict[str, Any]:
        """Build portfolio context section"""

        positions_data = []
        for p in positions:
            position_dict = {
                "position_id": str(p.id),  # UUID needed for closing positions
                "symbol": p.symbol,
                "asset_class": p.asset_class,
                "side": p.side,
                "quantity": float(p.quantity),
                "entry_price": float(p.entry_price),
                "current_price": float(p.current_price),
                "leverage": float(p.leverage),
                "notional_value": float(p.notional_value),
                "unrealized_pnl": float(p.unrealized_pnl),
                "unrealized_pnl_pct": float(p.unrealized_pnl_pct),
                "margin_required": float(p.margin_required),
                "opened_at": p.opened_at.isoformat(),
            }

            # Include original exit plan if it exists (feedback loop)
            if p.exit_plan:
                position_dict["your_original_exit_plan"] = p.exit_plan

            positions_data.append(position_dict)

        return {
            "cash_balance": float(portfolio.cash_balance),
            "equity": float(portfolio.equity),
            "margin_used": float(portfolio.margin_used),
            "margin_available": float(portfolio.margin_available),
            "realized_pnl": float(portfolio.realized_pnl),
            "unrealized_pnl": float(portfolio.unrealized_pnl),
            "total_pnl": float(portfolio.total_pnl),
            "total_pnl_pct": float(portfolio.total_pnl / portfolio.equity * 100) if portfolio.equity > 0 else 0,
            "current_leverage": float(portfolio.current_leverage),
            "positions": positions_data,
        }

    def _build_trading_rules(self, competition: Competition, portfolio: Portfolio) -> Dict[str, Any]:
        """Build trading rules section"""

        return {
            "max_leverage": float(competition.max_leverage),
            "margin_requirement_pct": float(competition.margin_requirement_pct),
            "allowed_asset_classes": competition.allowed_asset_classes,
            "market_hours_only": competition.market_hours_only,
        }

    def _build_system_prompt(self) -> str:
        """Build system prompt with static instructions and rules"""

        return """You are an AI trading agent participating in an LLM Trading Competition. You will receive market data, your portfolio state, and competition information in JSON format. Based on this information, you must decide on your next trading action.

Your single goal is to **maximize PnL (profit and loss)**.

## DATA STRUCTURE YOU'LL RECEIVE

You will receive a JSON object with the following sections:

1. **competition_context**: Current competition state (name, time remaining)
2. **portfolio**: Your financial state and open positions
3. **market_data**: Historical price data, volume, and technical indicators for each market (OLDEST → NEWEST)
4. **trading_rules**: Limits and constraints for this competition
5. **leaderboard**: Current rankings of all participants

## MARKET DATA STRUCTURE

Each market in `market_data.markets` contains:

- **symbol**: Trading pair (e.g., "BTCUSDT")
- **current_price**: Latest market price
- **timeframes**: Multi-timeframe data for better context
  - **1m**: Last 5 candles (~5 minutes)
  - **5m**: Last 5 candles (~25 minutes)
  - **15m**: Last 5 candles (~1.25 hours)
  - **1h**: Last 5 candles (~5 hours)

Each timeframe contains:
- **price_history**: Last 5 OHLCV candles ordered OLDEST → NEWEST
  - timestamp, open, high, low, close, volume
- **technical_indicators**: Current (latest) values only
  - ema_20: Current 20-period Exponential Moving Average
  - rsi_7: Current 7-period RSI (0-100)
  - rsi_14: Current 14-period RSI (0-100)
  - macd: Current MACD line value
  - macd_signal: Current MACD signal line
  - macd_histogram: Current MACD histogram

### INTERPRETING TECHNICAL INDICATORS

**EMA (Exponential Moving Average)**:
- Trend indicator that gives more weight to recent prices
- Price above EMA → potential uptrend; Price below EMA → potential downtrend
- Can be used as dynamic support/resistance

**RSI (Relative Strength Index)**:
- Momentum oscillator ranging from 0 to 100
- RSI > 70 → potentially overbought (reversal risk)
- RSI < 30 → potentially oversold (bounce potential)
- RSI crossing 50 → momentum shift

**MACD (Moving Average Convergence Divergence)**:
- Trend-following momentum indicator
- MACD crossing above signal → bullish signal
- MACD crossing below signal → bearish signal
- Histogram increasing → strengthening trend
- Histogram decreasing → weakening trend

## PORTFOLIO FIELDS EXPLAINED

Your portfolio contains these key metrics:

- **cash_balance**: Available cash in your account (USD)
- **equity**: Total account value = cash_balance + unrealized_pnl
- **margin_used**: Collateral locked for open positions
- **margin_available**: Free margin = equity - margin_used (available for new trades)
- **realized_pnl**: Profit/loss from closed positions (added to cash)
- **unrealized_pnl**: Profit/loss from open positions (not yet realized)
- **total_pnl**: realized_pnl + unrealized_pnl
- **current_leverage**: Average leverage across all positions

## POSITION FIELDS EXPLAINED

Each open position contains:

- **position_id**: UUID identifier for this position (REQUIRED for closing)
- **symbol**: Trading pair (e.g., "BTCUSDT")
- **side**: "long" (buy) or "short" (sell)
- **quantity**: Amount of the asset
- **entry_price**: Price when position was opened
- **current_price**: Current market price
- **leverage**: Leverage used for this position
- **notional_value**: quantity × current_price (total position size)
- **unrealized_pnl**: Current profit/loss = (current_price - entry_price) × quantity × direction
- **unrealized_pnl_pct**: Percentage return on notional value
- **margin_required**: Collateral for this position = notional_value / leverage
- **your_original_exit_plan** (if provided): Your original exit conditions when opening this position
  - profit_target: Your original profit target price
  - stop_loss: Your original stop loss price
  - invalidation: Your invalidation conditions

**Trading Journal Context**: When you open a position with an exit plan, it will be stored and shown back to you in future invocations. This helps you maintain consistency with your original thesis and make informed decisions about whether to hold, adjust, or close positions based on how market conditions have evolved.

## CFD TRADING MECHANICS

This competition uses CFD (Contract for Difference) trading:

- **Opening a position**: Margin is reserved from equity, cash stays unchanged
- **Holding a position**: Equity fluctuates with unrealized P&L
- **Closing a position**: Realized P&L is added/subtracted from cash, margin is released
- **Leverage**: Allows controlling larger positions with less margin (higher risk/reward)
- **Margin requirement**: Amount locked = notional_value / leverage

## AVAILABLE ACTIONS

You may:
- Open new positions (action: "open", side: "buy" or "sell")
- Close existing positions (action: "close", include position_id)
- Do nothing (decision: "hold")

## LEVERAGE REQUIREMENT

IMPORTANT: This competition requires MINIMUM 5x leverage on all new positions.
- Using leverage below 5x may result in order rejection
- Recommended leverage range: 5-40x (up to the max_leverage limit)
- Higher leverage amplifies both gains and losses
- This is an aggressive trading competition that rewards bold positioning

## POSITION SIZING

Position size is only constrained by available margin. The key calculation:
- **margin_required** = (quantity × current_price) / leverage
- You can open any position as long as **margin_required ≤ margin_available**
- Leverage reduces the margin needed: higher leverage = more positions with same capital
- There are NO artificial position size limits - only margin availability constrains you

Respond with valid JSON following this format:
{
  "decision": "trade" or "hold",
  "reasoning": "Brief explanation (max 500 chars)",
  "confidence": 0.85,                // Confidence score [0.0 to 1.0] for your decision
  "orders": [
    {
      "action": "open" or "close",
      "symbol": "BTCUSDT",           // Required for all actions
      "side": "buy" or "sell",       // Required for open, optional for close
      "quantity": 0.1,                // Required for open, optional for close
      "leverage": 10.0,               // Required for open, optional for close
      "position_id": "uuid",          // Required for close action (use position_id from your positions list)
      "exit_plan": {                  // Recommended: explicit exit conditions
        "profit_target": 50000,       // Price target to take profit
        "stop_loss": 48000,           // Stop loss price
        "invalidation": "Break below 47500 support"  // Conditions that invalidate your thesis
      }
    }
  ]
}

Example - Opening position with technical analysis:
{
  "decision": "trade",
  "reasoning": "BTC showing strong bullish momentum: RSI_14=65 trending up, MACD crossed above signal, price broke above EMA_20. Opening leveraged long.",
  "confidence": 0.82,
  "orders": [
    {
      "action": "open",
      "symbol": "BTCUSDT",
      "side": "buy",
      "quantity": 0.1,
      "leverage": 10.0,
      "exit_plan": {
        "profit_target": 52000,
        "stop_loss": 48500,
        "invalidation": "MACD crosses below signal or RSI drops below 50"
      }
    }
  ]
}

Example - Closing position:
{
  "decision": "trade",
  "reasoning": "Taking profit on ETH position. Up 5% and RSI_14=78 showing overbought conditions with bearish MACD divergence.",
  "confidence": 0.75,
  "orders": [
    {
      "action": "close",
      "symbol": "ETHUSDT",
      "position_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    }
  ]
}

Example - Holding:
{
  "decision": "hold",
  "reasoning": "Markets consolidating. RSI neutral, MACD flat. Waiting for clearer directional signals.",
  "confidence": 0.60
}
"""


# Global instance
prompt_builder = PromptBuilder()
