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

        # Calculate maximum position size in dollars
        max_position_size_dollars = float(portfolio.equity * competition.max_position_size_pct / 100)

        return {
            "max_leverage": float(competition.max_leverage),
            "max_position_size_pct": float(competition.max_position_size_pct),
            "max_position_size_dollars": max_position_size_dollars,
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
- Recommended leverage range: 5-10x
- Higher leverage amplifies both gains and losses
- This is an aggressive trading competition that rewards bold positioning

CRITICAL - POSITION SIZING RULES:
The system validates that (quantity × current_price) ≤ max_position_size_dollars

1. NOTIONAL VALUE LIMIT (enforced by system):
   - max_position_size_dollars is the maximum NOTIONAL VALUE per position
   - Notional value = quantity × current_price
   - This limit applies REGARDLESS of leverage
   - Example: If max is $5000 and BTC is $100,000, max quantity = 5000/100000 = 0.05 BTC

2. LEVERAGE DOES NOT AFFECT POSITION SIZE LIMITS:
   - Leverage only affects margin required: margin = notional_value / leverage
   - Higher leverage = lower margin required, but same notional value limit
   - Example: $5000 notional with 2x leverage requires $2500 margin
   - Example: $5000 notional with 1x leverage requires $5000 margin

3. CALCULATION FORMULA (use this):
   - max_quantity = max_position_size_dollars / current_price
   - Always calculate: notional_value = quantity × current_price
   - Verify: notional_value ≤ max_position_size_dollars
   - Add safety buffer: use 98% of max to account for price slippage

4. WORKED EXAMPLE:
   - Given: max_position_size_dollars = $5000, BTC price = $100,000
   - Max quantity = 5000 / 100000 = 0.05 BTC
   - Safe quantity (98%) = 0.05 × 0.98 = 0.049 BTC
   - Notional value check: 0.049 × 100000 = $4900 ✓ (under $5000 limit)
   - At 2x leverage: margin required = 4900 / 2 = $2450
   - At 3x leverage: margin required = 4900 / 3 = $1633

COMMON MISTAKES TO AVOID:
❌ DO NOT: Calculate quantity as (max_position_size × leverage) / price
✓ DO: Calculate quantity as max_position_size / price
❌ DO NOT: Assume leverage increases position size limit
✓ DO: Understand leverage only reduces margin requirement

Respond with valid JSON following this format:
{
  "decision": "trade" or "hold",
  "reasoning": "Brief explanation (max 500 chars)",
  "orders": [
    {
      "action": "open" or "close",
      "symbol": "BTCUSDT",
      "side": "buy" or "sell",
      "quantity": 0.049,
      "leverage": 2.0,
      "position_id": "uuid" // Only for close action
    }
  ]
}

Example - Opening position (max_position_size_dollars = $5000, BTC = $100,000):
{
  "decision": "trade",
  "reasoning": "BTC momentum strong. Opening conservative long position within limits.",
  "orders": [
    {
      "action": "open",
      "symbol": "BTCUSDT",
      "side": "buy",
      "quantity": 0.049,
      "leverage": 2.0
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
