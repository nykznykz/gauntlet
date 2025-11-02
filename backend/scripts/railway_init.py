#!/usr/bin/env python3
"""
Railway Deployment Initialization Script

This script runs after migrations on Railway deployment.
It initializes a fresh competition with participants if none exist.

Safe to run multiple times - only creates data if database is empty.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.competition import Competition
from app.models.participant import Participant
from app.models.portfolio import Portfolio
from app.models.portfolio_history import PortfolioHistory


# ============================================================================
# CONFIGURATION
# ============================================================================

COMPETITION_CONFIG = {
    "name": "LLM Trading Competition - Battle Royale",
    "description": "A competitive trading simulation where different LLM agents compete to maximize returns using CFD trading strategies.",
    "initial_capital": Decimal("10000.00"),
    "max_leverage": Decimal("40.0"),  # Max 40x leverage (implies 2.5% margin requirement)
    "maintenance_margin_pct": Decimal("1.25"),  # 1.25% maintenance margin (half of margin requirement)
    "allowed_asset_classes": ["crypto"],
    "max_participants": 20,
    "invocation_interval_minutes": 5,
    "market_hours_only": False,
    "duration_days": 7,
}

PARTICIPANTS_CONFIG = [
    {
        "name": "claude-sonnet-4.5",
        "llm_provider": "anthropic",
        "llm_model": "claude-3-5-sonnet-20250110",  # Sonnet 4.5
        "llm_config": {
            "temperature": 0.7,
            "max_tokens": 2000,
        }
    },
    {
        "name": "gpt4o",
        "llm_provider": "azure_openai",
        "llm_model": "gpt-4o",
        "llm_config": {
            "model": "gpt-4o",
            "temperature": 0.7,
            "max_tokens": 2000,
        }
    },
    {
        "name": "gpt4o-mini",
        "llm_provider": "azure_openai",
        "llm_model": "gpt-4o-mini",
        "llm_config": {
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 2000,
        }
    },
    {
        "name": "deepseek-chat",
        "llm_provider": "deepseek",
        "llm_model": "deepseek-chat",
        "llm_config": {
            "temperature": 0.7,
            "max_tokens": 4096,
        }
    },
]


def create_competition(db: Session) -> Competition:
    """Create a new competition"""
    print("📊 Creating competition...")

    now = datetime.now(timezone.utc)
    config = COMPETITION_CONFIG

    competition = Competition(
        name=config["name"],
        description=config["description"],
        status="active",
        start_time=now,
        end_time=now + timedelta(days=config["duration_days"]),
        initial_capital=config["initial_capital"],
        max_leverage=config["max_leverage"],
        maintenance_margin_pct=config["maintenance_margin_pct"],
        allowed_asset_classes=config["allowed_asset_classes"],
        max_participants=config["max_participants"],
        invocation_interval_minutes=config["invocation_interval_minutes"],
        market_hours_only=config["market_hours_only"],
    )

    db.add(competition)
    db.commit()
    db.refresh(competition)

    print(f"✅ Created: {competition.name}")
    print(f"   ID: {competition.id}")
    print(f"   Initial Capital: ${config['initial_capital']}")
    print(f"   Duration: {config['duration_days']} days")

    return competition


def create_participants(db: Session, competition: Competition) -> list:
    """Create participants and portfolios"""
    print(f"👥 Creating {len(PARTICIPANTS_CONFIG)} participants...")

    participants = []

    for p_config in PARTICIPANTS_CONFIG:
        # Create participant
        participant = Participant(
            competition_id=competition.id,
            name=p_config["name"],
            llm_provider=p_config["llm_provider"],
            llm_model=p_config["llm_model"],
            llm_config=p_config["llm_config"],
            initial_capital=competition.initial_capital,
            current_equity=competition.initial_capital,
            peak_equity=competition.initial_capital,
            status="active",
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
        )

        db.add(participant)
        db.flush()

        # Create portfolio
        portfolio = Portfolio(
            participant_id=participant.id,
            cash_balance=competition.initial_capital,
            equity=competition.initial_capital,
            margin_used=Decimal("0.0"),
            margin_available=competition.initial_capital,
            unrealized_pnl=Decimal("0.0"),
            realized_pnl=Decimal("0.0"),
            total_pnl=Decimal("0.0"),
        )

        db.add(portfolio)

        # Initial history entry
        history = PortfolioHistory(
            participant_id=participant.id,
            equity=competition.initial_capital,
            cash_balance=competition.initial_capital,
            margin_used=Decimal("0.0"),
            realized_pnl=Decimal("0.0"),
            unrealized_pnl=Decimal("0.0"),
            total_pnl=Decimal("0.0"),
        )

        db.add(history)
        participants.append(participant)

        print(f"   - {participant.name} ({participant.llm_provider}/{participant.llm_model})")

    db.commit()
    print(f"✅ Created {len(participants)} participants")

    return participants


def main():
    """Main execution - idempotent, safe to run multiple times"""
    print("="*60)
    print("🚀 Railway Deployment Initialization")
    print("="*60)

    db = SessionLocal()

    try:
        # Check if competition already exists
        existing_competition = db.query(Competition).first()

        if existing_competition:
            print("✓ Competition already exists")
            print(f"  Name: {existing_competition.name}")
            print(f"  Status: {existing_competition.status}")

            # Check participants
            participant_count = db.query(Participant).count()
            print(f"✓ {participant_count} participants registered")
            print("="*60)
            print("Skipping initialization (data already exists)")
            return

        # No competition exists - create fresh setup
        print("No competition found - initializing fresh setup...")
        print()

        competition = create_competition(db)
        participants = create_participants(db, competition)

        print()
        print("="*60)
        print("🎉 Initialization Complete!")
        print("="*60)
        print(f"Competition: {competition.name}")
        print(f"Participants: {len(participants)}")
        print(f"Status: {competition.status}")
        print("="*60)

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
