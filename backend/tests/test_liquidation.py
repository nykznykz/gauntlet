"""Tests for liquidation mechanism"""
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch
import pytest
from app.services.portfolio_manager import PortfolioManager
from app.models.portfolio import Portfolio
from app.models.participant import Participant
from app.models.competition import Competition
from app.models.position import Position


def test_check_and_liquidate_when_margin_level_too_low():
    """Test that participant is liquidated when margin level drops below threshold"""
    # Setup
    mock_db = Mock()
    portfolio_manager = PortfolioManager(mock_db)

    # Create mock competition
    competition = Mock(spec=Competition)
    competition.max_leverage = Decimal("10")  # 10x leverage = 10% initial margin
    competition.maintenance_margin_pct = Decimal("5")  # 5% maintenance margin
    # Liquidation threshold = (5 / 10) * 100 = 50%

    # Create mock participant (active)
    participant = Mock(spec=Participant)
    participant.status = "active"
    participant.id = "participant-123"
    participant.competition_id = "comp-123"

    # Create mock portfolio with margin level below threshold
    # equity = 4000, margin_used = 10000
    # margin_level = (4000 / 10000) * 100 = 40% < 50% threshold
    portfolio = Mock(spec=Portfolio)
    portfolio.id = "portfolio-123"
    portfolio.equity = Decimal("4000")
    portfolio.margin_used = Decimal("10000")
    portfolio.cash_balance = Decimal("3000")
    portfolio.realized_pnl = Decimal("-1000")

    # Create mock positions
    position1 = Mock(spec=Position)
    position1.id = "pos-1"
    position1.symbol = "BTCUSDT"
    position1.asset_class = "crypto"

    position2 = Mock(spec=Position)
    position2.id = "pos-2"
    position2.symbol = "ETHUSDT"
    position2.asset_class = "crypto"

    # Mock database query to return positions
    mock_result = Mock()
    mock_result.scalars().all.return_value = [position1, position2]
    mock_db.execute.return_value = mock_result

    # Mock CFD engine and market data service
    with patch('app.services.cfd_engine.CFDEngine') as MockCFDEngine, \
         patch('app.services.market_data_service.market_data_service') as mock_market_data:

        # Setup mock CFD engine
        mock_cfd_engine = Mock()
        MockCFDEngine.return_value = mock_cfd_engine

        # Mock close_position results
        mock_cfd_engine.close_position.side_effect = [
            {
                "realized_pnl": Decimal("-500"),
                "realized_pnl_pct": Decimal("-10"),
                "margin_released": Decimal("5000")
            },
            {
                "realized_pnl": Decimal("-300"),
                "realized_pnl_pct": Decimal("-6"),
                "margin_released": Decimal("5000")
            }
        ]

        # Mock market data service
        mock_market_data.get_price.return_value = Decimal("45000")

        # Mock update_portfolio to avoid actual DB operations
        portfolio_manager.update_portfolio = Mock(return_value=portfolio)

        # Execute
        was_liquidated = portfolio_manager.check_and_liquidate(participant, portfolio, competition)

        # Assert
        assert was_liquidated is True
        assert participant.status == "liquidated"
        mock_db.add.assert_called()  # Portfolio and participant were added to session
        mock_db.commit.assert_called()  # Transaction was committed

        # Verify both positions were closed
        assert mock_cfd_engine.close_position.call_count == 2

        # Verify cash balance was updated with realized P&L
        expected_total_pnl = Decimal("-500") + Decimal("-300")
        assert portfolio.cash_balance == Decimal("3000") + expected_total_pnl
        assert portfolio.realized_pnl == Decimal("-1000") + expected_total_pnl


def test_check_and_liquidate_no_liquidation_when_margin_level_ok():
    """Test that participant is NOT liquidated when margin level is healthy"""
    # Setup
    mock_db = Mock()
    portfolio_manager = PortfolioManager(mock_db)

    # Create mock competition
    competition = Mock(spec=Competition)
    competition.max_leverage = Decimal("10")  # 10x leverage = 10% initial margin
    competition.maintenance_margin_pct = Decimal("5")  # 5% maintenance margin
    # Liquidation threshold = (5 / 10) * 100 = 50%

    # Create mock participant (active)
    participant = Mock(spec=Participant)
    participant.status = "active"

    # Create mock portfolio with margin level ABOVE threshold
    # equity = 8000, margin_used = 10000
    # margin_level = (8000 / 10000) * 100 = 80% > 50% threshold
    portfolio = Mock(spec=Portfolio)
    portfolio.equity = Decimal("8000")
    portfolio.margin_used = Decimal("10000")

    # Execute
    was_liquidated = portfolio_manager.check_and_liquidate(participant, portfolio, competition)

    # Assert
    assert was_liquidated is False
    assert participant.status == "active"  # Status unchanged


def test_check_and_liquidate_skips_already_liquidated_participant():
    """Test that already liquidated participants are skipped"""
    # Setup
    mock_db = Mock()
    portfolio_manager = PortfolioManager(mock_db)

    # Create mock competition
    competition = Mock(spec=Competition)
    competition.max_leverage = Decimal("10")
    competition.maintenance_margin_pct = Decimal("5")

    # Create mock participant (already liquidated)
    participant = Mock(spec=Participant)
    participant.status = "liquidated"

    # Create mock portfolio (doesn't matter, should skip)
    portfolio = Mock(spec=Portfolio)
    portfolio.equity = Decimal("100")
    portfolio.margin_used = Decimal("10000")

    # Execute
    was_liquidated = portfolio_manager.check_and_liquidate(participant, portfolio, competition)

    # Assert
    assert was_liquidated is False


def test_check_and_liquidate_skips_when_no_margin_used():
    """Test that participants with no open positions are skipped"""
    # Setup
    mock_db = Mock()
    portfolio_manager = PortfolioManager(mock_db)

    # Create mock competition
    competition = Mock(spec=Competition)
    competition.max_leverage = Decimal("10")
    competition.maintenance_margin_pct = Decimal("5")

    # Create mock participant (active)
    participant = Mock(spec=Participant)
    participant.status = "active"

    # Create mock portfolio with NO margin used (no positions)
    portfolio = Mock(spec=Portfolio)
    portfolio.equity = Decimal("10000")
    portfolio.margin_used = Decimal("0")

    # Execute
    was_liquidated = portfolio_manager.check_and_liquidate(participant, portfolio, competition)

    # Assert
    assert was_liquidated is False
