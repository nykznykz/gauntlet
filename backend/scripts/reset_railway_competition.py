#!/usr/bin/env python3
"""
Reset Railway Competition Script

This script deletes the existing competition and all related data,
then runs railway_init.py to recreate a fresh competition.

WARNING: This deletes ALL competition data!
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.competition import Competition
from app.models.participant import Participant
from app.models.portfolio import Portfolio
from app.models.portfolio_history import PortfolioHistory
from app.models.position import Position
from app.models.trade import Trade
from app.models.invocation import Invocation


def delete_all_data(db: Session):
    """Delete all competition-related data"""
    print("🗑️  Deleting existing competition data...")

    # Delete in correct order to respect foreign key constraints
    deleted_counts = {}

    # Delete invocations
    count = db.query(Invocation).delete()
    deleted_counts['invocations'] = count
    print(f"   - Deleted {count} invocations")

    # Delete portfolio history
    count = db.query(PortfolioHistory).delete()
    deleted_counts['portfolio_history'] = count
    print(f"   - Deleted {count} portfolio history records")

    # Delete trades
    count = db.query(Trade).delete()
    deleted_counts['trades'] = count
    print(f"   - Deleted {count} trades")

    # Delete positions
    count = db.query(Position).delete()
    deleted_counts['positions'] = count
    print(f"   - Deleted {count} positions")

    # Delete portfolios
    count = db.query(Portfolio).delete()
    deleted_counts['portfolios'] = count
    print(f"   - Deleted {count} portfolios")

    # Delete participants
    count = db.query(Participant).delete()
    deleted_counts['participants'] = count
    print(f"   - Deleted {count} participants")

    # Delete competitions
    count = db.query(Competition).delete()
    deleted_counts['competitions'] = count
    print(f"   - Deleted {count} competitions")

    db.commit()
    print("✅ All data deleted successfully")

    return deleted_counts


def main():
    """Main execution"""
    print("="*60)
    print("🔄 Railway Competition Reset")
    print("="*60)
    print("WARNING: This will delete ALL competition data!")
    print("="*60)

    db = SessionLocal()

    try:
        # Delete all existing data
        deleted_counts = delete_all_data(db)

        print()
        print("="*60)
        print("✅ Reset Complete!")
        print("="*60)
        print(f"Total records deleted: {sum(deleted_counts.values())}")
        print()
        print("Now run: python scripts/railway_init.py")
        print("to recreate the competition with fresh data")
        print("="*60)

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
