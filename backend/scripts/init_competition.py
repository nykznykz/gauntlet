#!/usr/bin/env python3
"""
Competition Initialization Script

This script will:
1. Delete all existing competitions and participants (cascades to all related data)
2. Create a fresh competition
3. Register LLM participants
4. Initialize their portfolios

Usage:
    python scripts/init_competition.py
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.competition import Competition
from app.models.participant import Participant
from app.models.portfolio import Portfolio
from app.models.position import Position
from app.models.order import Order
from app.models.trade import Trade
from app.models.llm_invocation import LLMInvocation
from app.models.portfolio_history import PortfolioHistory


# ============================================================================
# CONFIGURATION - Modify these values as needed
# ============================================================================

COMPETITION_CONFIG = {
    "name": "LLM Trading Competition - Battle Royale",
    "description": "A competitive trading simulation where different LLM agents compete to maximize returns using CFD trading strategies.",
    "initial_capital": Decimal("10000.00"),
    "max_leverage": Decimal("10.0"),
    "margin_requirement_pct": Decimal("10.0"),  # 10% margin requirement
    "maintenance_margin_pct": Decimal("5.0"),   # 5% maintenance margin (liquidation threshold)
    "allowed_asset_classes": ["crypto"],  # Focus on crypto for now
    "max_position_size_pct": Decimal("50.0"),  # Max 50% of equity per position
    "max_participants": 20,
    "invocation_interval_minutes": 60,  # Invoke LLMs every hour
    "market_hours_only": False,  # Trade 24/7 for crypto
    "duration_days": 7,  # 7-day competition
}

PARTICIPANTS_CONFIG = [
    {
        "name": "claude-sonnet",
        "llm_provider": "anthropic",
        "llm_model": "claude-3-5-sonnet-20241022",
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
            "model": "gpt-4o",  # Azure deployment name
            "temperature": 0.7,
            "max_tokens": 2000,
        }
    },
    {
        "name": "gpt4o-mini",
        "llm_provider": "azure_openai",
        "llm_model": "gpt-4o-mini",
        "llm_config": {
            "model": "gpt-4o-mini",  # Azure deployment name
            "temperature": 0.7,
            "max_tokens": 2000,
        }
    },
    {
        "name": "deepseek-reasoner",
        "llm_provider": "deepseek",
        "llm_model": "deepseek-reasoner",
        "llm_config": {
            "temperature": 0.7,
            "max_tokens": 2000,
        }
    },
]


# ============================================================================
# Script Functions
# ============================================================================

def delete_all_data(db: Session):
    """Delete all existing competitions and related data"""
    print("\n🗑️  Deleting all existing data...")

    # Delete in order to avoid foreign key constraints
    # (though CASCADE should handle this, being explicit is safer)
    deleted_counts = {}

    deleted_counts['portfolio_history'] = db.query(PortfolioHistory).delete()
    deleted_counts['invocations'] = db.query(LLMInvocation).delete()
    deleted_counts['trades'] = db.query(Trade).delete()
    deleted_counts['orders'] = db.query(Order).delete()
    deleted_counts['positions'] = db.query(Position).delete()
    deleted_counts['portfolios'] = db.query(Portfolio).delete()
    deleted_counts['participants'] = db.query(Participant).delete()
    deleted_counts['competitions'] = db.query(Competition).delete()

    db.commit()

    print("   Deleted:")
    for table, count in deleted_counts.items():
        if count > 0:
            print(f"   - {count} {table}")

    if sum(deleted_counts.values()) == 0:
        print("   - No existing data found")

    return deleted_counts


def create_competition(db: Session, config: dict) -> Competition:
    """Create a new competition"""
    print("\n📊 Creating new competition...")

    now = datetime.now(timezone.utc)

    competition = Competition(
        name=config["name"],
        description=config["description"],
        status="active",  # Start immediately
        start_time=now,
        end_time=now + timedelta(days=config["duration_days"]),
        initial_capital=config["initial_capital"],
        max_leverage=config["max_leverage"],
        margin_requirement_pct=config["margin_requirement_pct"],
        maintenance_margin_pct=config["maintenance_margin_pct"],
        allowed_asset_classes=config["allowed_asset_classes"],
        max_position_size_pct=config["max_position_size_pct"],
        max_participants=config["max_participants"],
        invocation_interval_minutes=config["invocation_interval_minutes"],
        market_hours_only=config["market_hours_only"],
    )

    db.add(competition)
    db.commit()
    db.refresh(competition)

    print(f"   ✅ Created competition: {competition.name}")
    print(f"   - ID: {competition.id}")
    print(f"   - Duration: {config['duration_days']} days")
    print(f"   - Initial Capital: ${config['initial_capital']}")
    print(f"   - Max Leverage: {config['max_leverage']}x")
    print(f"   - Margin Requirement: {config['margin_requirement_pct']}%")
    print(f"   - Maintenance Margin: {config['maintenance_margin_pct']}%")
    print(f"   - Invocation Interval: {config['invocation_interval_minutes']} minutes")

    return competition


def create_participants(db: Session, competition: Competition, participants_config: list) -> list:
    """Create and register participants"""
    print(f"\n👥 Registering {len(participants_config)} participants...")

    participants = []

    for i, p_config in enumerate(participants_config, 1):
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
        db.flush()  # Get participant ID

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

        # Create initial portfolio history entry
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

        print(f"   {i}. {participant.name} ({participant.llm_provider}/{participant.llm_model})")

    db.commit()

    print(f"   ✅ Registered {len(participants)} participants")

    return participants


def print_summary(competition: Competition, participants: list):
    """Print a summary of the initialization"""
    print("\n" + "="*80)
    print("🎉 COMPETITION INITIALIZED SUCCESSFULLY!")
    print("="*80)
    print(f"\n📊 Competition: {competition.name}")
    print(f"   ID: {competition.id}")
    print(f"   Status: {competition.status}")
    print(f"   Duration: {competition.start_time.strftime('%Y-%m-%d %H:%M')} → {competition.end_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"\n💰 Trading Parameters:")
    print(f"   Initial Capital: ${competition.initial_capital}")
    print(f"   Max Leverage: {competition.max_leverage}x")
    print(f"   Margin Requirement: {competition.margin_requirement_pct}%")
    print(f"   Maintenance Margin: {competition.maintenance_margin_pct}%")
    print(f"   Allowed Asset Classes: {', '.join(competition.allowed_asset_classes)}")
    print(f"\n👥 Participants ({len(participants)}):")
    for p in participants:
        print(f"   - {p.name} ({p.llm_provider}/{p.llm_model})")
    print(f"\n⏰ Scheduler:")
    print(f"   LLM Invocation Interval: Every {competition.invocation_interval_minutes} minutes")
    print(f"\n🌐 Access:")
    print(f"   API: http://localhost:8000/docs")
    print(f"   Frontend: http://localhost:3000")
    print("\n" + "="*80)


def main():
    """Main script execution"""
    print("="*80)
    print("🚀 LLM TRADING COMPETITION - INITIALIZATION SCRIPT")
    print("="*80)

    # Create database session
    db = SessionLocal()

    try:
        # Step 1: Delete all existing data
        delete_all_data(db)

        # Step 2: Create new competition
        competition = create_competition(db, COMPETITION_CONFIG)

        # Step 3: Create participants
        participants = create_participants(db, competition, PARTICIPANTS_CONFIG)

        # Step 4: Print summary
        print_summary(competition, participants)

        print("\n✅ Initialization complete! You can now:")
        print("   1. Start the backend: uvicorn app.main:app --reload")
        print("   2. Start the frontend: npm run dev (in frontend/)")
        print("   3. Visit http://localhost:3000 to view the dashboard")
        print("\n💡 The scheduler will automatically invoke LLMs based on the interval.")

    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
