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

        positions_data = [
            {
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
            for p in positions
        ]

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

## DATA STRUCTURE YOU'LL RECEIVE

You will receive a JSON object with the following sections:

1. **competition_context**: Current competition state (name, time remaining)
2. **portfolio**: Your financial state and open positions
3. **market_data**: Current prices for available trading symbols
4. **trading_rules**: Limits and constraints for this competition
5. **leaderboard**: Current rankings of all participants

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
  "orders": [
    {
      "action": "open" or "close",
      "symbol": "BTCUSDT",           // Required for all actions
      "side": "buy" or "sell",       // Required for open, optional for close
      "quantity": 0.1,                // Required for open, optional for close
      "leverage": 10.0,               // Required for open, optional for close
      "position_id": "uuid"           // Required for close action (use position_id from your positions list)
    }
  ]
}

Example - Opening position:
{
  "decision": "trade",
  "reasoning": "BTC showing strong bullish momentum. Opening leveraged long position.",
  "orders": [
    {
      "action": "open",
      "symbol": "BTCUSDT",
      "side": "buy",
      "quantity": 0.1,
      "leverage": 10.0
    }
  ]
}

Example - Closing position:
{
  "decision": "trade",
  "reasoning": "Taking profit on ETH position. Up 5% and showing signs of reversal.",
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
  "reasoning": "Waiting for clearer market direction. Current positions look stable."
}
"""


# Global instance
prompt_builder = PromptBuilder()
