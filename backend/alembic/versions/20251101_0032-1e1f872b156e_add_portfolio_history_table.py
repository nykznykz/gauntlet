"""add portfolio history table

Revision ID: 1e1f872b156e
Revises: 35b27664f34b
Create Date: 2025-11-01 00:32:32.456693

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1e1f872b156e'
down_revision = '35b27664f34b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create portfolio_history table
    op.create_table(
        'portfolio_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('participant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('equity', sa.Numeric(20, 2), nullable=False),
        sa.Column('cash_balance', sa.Numeric(20, 2), nullable=False),
        sa.Column('margin_used', sa.Numeric(20, 2), nullable=False),
        sa.Column('realized_pnl', sa.Numeric(20, 2), nullable=False),
        sa.Column('unrealized_pnl', sa.Numeric(20, 2), nullable=False),
        sa.Column('total_pnl', sa.Numeric(20, 2), nullable=False),
        sa.Column('recorded_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['participant_id'], ['participants.id'], ondelete='CASCADE'),
    )

    # Create index for querying by participant and time
    op.create_index(
        'idx_portfolio_history_participant_time',
        'portfolio_history',
        ['participant_id', 'recorded_at']
    )


def downgrade() -> None:
    # Drop index
    op.drop_index('idx_portfolio_history_participant_time', table_name='portfolio_history')

    # Drop table
    op.drop_table('portfolio_history')
