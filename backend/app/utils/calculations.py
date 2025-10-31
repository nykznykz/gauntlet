"""Financial calculation utilities"""
from decimal import Decimal
from typing import Literal


def calculate_notional_value(quantity: Decimal, price: Decimal) -> Decimal:
    """Calculate notional value of a position"""
    return quantity * price


def calculate_margin_required(notional_value: Decimal, leverage: Decimal) -> Decimal:
    """Calculate margin required for a position"""
    return notional_value / leverage


def calculate_unrealized_pnl_long(
    quantity: Decimal,
    entry_price: Decimal,
    current_price: Decimal
) -> Decimal:
    """Calculate unrealized P&L for a long position"""
    return quantity * (current_price - entry_price)


def calculate_unrealized_pnl_short(
    quantity: Decimal,
    entry_price: Decimal,
    current_price: Decimal
) -> Decimal:
    """Calculate unrealized P&L for a short position"""
    return quantity * (entry_price - current_price)


def calculate_unrealized_pnl(
    side: Literal["long", "short"],
    quantity: Decimal,
    entry_price: Decimal,
    current_price: Decimal
) -> Decimal:
    """Calculate unrealized P&L based on position side"""
    if side == "long":
        return calculate_unrealized_pnl_long(quantity, entry_price, current_price)
    else:
        return calculate_unrealized_pnl_short(quantity, entry_price, current_price)


def calculate_pnl_percentage(pnl: Decimal, entry_value: Decimal) -> Decimal:
    """Calculate P&L as percentage"""
    if entry_value == 0:
        return Decimal("0")
    return (pnl / entry_value) * Decimal("100")


def calculate_equity(cash_balance: Decimal, unrealized_pnl: Decimal) -> Decimal:
    """Calculate total equity"""
    return cash_balance + unrealized_pnl


def calculate_margin_level(equity: Decimal, margin_used: Decimal) -> Decimal:
    """Calculate margin level percentage"""
    if margin_used == 0:
        return Decimal("9999")  # Effectively infinite
    return (equity / margin_used) * Decimal("100")


def calculate_current_leverage(total_notional_value: Decimal, equity: Decimal) -> Decimal:
    """Calculate current leverage ratio"""
    if equity == 0:
        return Decimal("0")
    return total_notional_value / equity


def check_liquidation(
    margin_level: Decimal,
    maintenance_margin_pct: Decimal,
    initial_margin_pct: Decimal
) -> bool:
    """Check if position should be liquidated"""
    liquidation_threshold = (maintenance_margin_pct / initial_margin_pct) * Decimal("100")
    return margin_level < liquidation_threshold


def calculate_max_position_size(
    equity: Decimal,
    max_position_size_pct: Decimal
) -> Decimal:
    """Calculate maximum allowed position notional value"""
    return equity * (max_position_size_pct / Decimal("100"))


def calculate_win_rate(winning_trades: int, total_trades: int) -> Decimal:
    """Calculate win rate percentage"""
    if total_trades == 0:
        return Decimal("0")
    return Decimal(str(winning_trades / total_trades * 100))
