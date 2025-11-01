"""Check participant invocations and execution results"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.participant import Participant
from app.models.llm_invocation import LLMInvocation
from app.models.order import Order
from app.models.position import Position
from sqlalchemy import desc

# Get participant name from command line or default
participant_name = sys.argv[1] if len(sys.argv) > 1 else "gpt%mini%"

# Create database session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Find participant
    participant = db.query(Participant).filter(
        Participant.name.ilike(f"%{participant_name}%")
    ).first()

    if not participant:
        print(f"Participant matching '{participant_name}' not found")
        print("\nAvailable participants:")
        all_participants = db.query(Participant).all()
        for p in all_participants:
            print(f"  - {p.name}")
        sys.exit(1)

    print(f"=== Participant: {participant.name} ===")
    print(f"ID: {participant.id}")
    print(f"Provider: {participant.llm_provider}")
    print(f"Model: {participant.llm_config.get('model', 'N/A') if participant.llm_config else 'N/A'}")
    print(f"Status: {participant.status}")
    print(f"Current Equity: ${participant.current_equity}")
    print()

    # Check invocations
    invocations = db.query(LLMInvocation).filter(
        LLMInvocation.participant_id == participant.id
    ).order_by(desc(LLMInvocation.invocation_time)).limit(10).all()

    print(f"=== Recent Invocations (last 10) ===")
    for inv in invocations:
        print(f"\nInvocation ID: {inv.id}")
        print(f"  Time: {inv.invocation_time}")
        print(f"  Status: {inv.status}")
        if inv.error_message:
            print(f"  Error: {inv.error_message}")
        if inv.parsed_decision:
            print(f"  Decision: {inv.parsed_decision.get('decision', 'N/A')}")
            print(f"  Reasoning: {inv.parsed_decision.get('reasoning', 'N/A')[:100]}")
            orders = inv.parsed_decision.get('orders', [])
            print(f"  Orders in decision: {len(orders)}")
            for idx, order in enumerate(orders):
                print(f"    Order {idx+1}: {order.get('action')} {order.get('symbol')} - side: {order.get('side')}, qty: {order.get('quantity')}")
        if inv.execution_results:
            print(f"  Execution Results:")
            for idx, result in enumerate(inv.execution_results):
                print(f"    Result {idx+1}:")
                print(f"      Order ID: {result.get('order_id')}")
                print(f"      Action: {result.get('action')} {result.get('symbol')}")
                print(f"      Validation: {'✓ Passed' if result.get('validation_passed') else '✗ Failed'}")
                if result.get('rejection_reason'):
                    print(f"      Rejection: {result.get('rejection_reason')}")
                print(f"      Status: {result.get('status')}")
                if result.get('executed_price'):
                    print(f"      Executed Price: ${result.get('executed_price')}")

    print()

    # Check orders
    orders = db.query(Order).filter(
        Order.participant_id == participant.id
    ).order_by(desc(Order.created_at)).limit(10).all()

    print(f"=== Orders (last 10) ===")
    for order in orders:
        print(f"\nOrder ID: {order.id}")
        print(f"  Created: {order.created_at}")
        print(f"  Symbol: {order.symbol}")
        print(f"  Side: {order.side}")
        print(f"  Quantity: {order.quantity}")
        print(f"  Leverage: {order.leverage}")
        print(f"  Status: {order.status}")
        if order.rejection_reason:
            print(f"  Rejection Reason: {order.rejection_reason}")
        if order.executed_at:
            print(f"  Executed: {order.executed_at}")
            print(f"  Executed Price: {order.executed_price}")

    print()

    # Check positions
    positions = db.query(Position).filter(
        Position.participant_id == participant.id
    ).all()

    print(f"=== Positions ===")
    if positions:
        for pos in positions:
            print(f"\nPosition ID: {pos.id}")
            print(f"  Symbol: {pos.symbol}")
            print(f"  Direction: {pos.direction}")
            print(f"  Quantity: {pos.quantity}")
            print(f"  Entry Price: {pos.entry_price}")
            print(f"  Leverage: {pos.leverage}")
            print(f"  Status: {pos.status}")
    else:
        print("No positions found")

finally:
    db.close()
