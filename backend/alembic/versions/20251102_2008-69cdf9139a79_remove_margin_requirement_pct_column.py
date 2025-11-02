"""remove_margin_requirement_pct_and_max_position_size_pct

Revision ID: 69cdf9139a79
Revises: 34a666f12d78
Create Date: 2025-11-02 20:08:08.222494

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '69cdf9139a79'
down_revision = '34a666f12d78'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop old check constraint that references margin_requirement_pct
    op.drop_constraint('valid_margin', 'competitions', type_='check')

    # Drop redundant columns (derived or unrealistic)
    op.drop_column('competitions', 'margin_requirement_pct')
    op.drop_column('competitions', 'max_position_size_pct')

    # Add new check constraint using derived margin requirement
    op.create_check_constraint(
        'valid_margin',
        'competitions',
        'maintenance_margin_pct < (100.0 / max_leverage)'
    )


def downgrade() -> None:
    # Drop the new check constraint
    op.drop_constraint('valid_margin', 'competitions', type_='check')

    # Add back the removed columns
    op.add_column('competitions',
        sa.Column('margin_requirement_pct', sa.Numeric(5, 2), nullable=False, server_default='10.00')
    )
    op.add_column('competitions',
        sa.Column('max_position_size_pct', sa.Numeric(5, 2), nullable=False, server_default='20.00')
    )

    # Restore old check constraint
    op.create_check_constraint(
        'valid_margin',
        'competitions',
        'maintenance_margin_pct < margin_requirement_pct'
    )
