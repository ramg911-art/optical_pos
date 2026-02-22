"""add advance/balance payment columns to sales

Revision ID: 20260222
Revises: 20260218_01
Create Date: 2026-02-22

Adds advance_amount, balance_amount, payment_status, delivery_status and related
columns to sales table. Additive only - no drops or modifications.
"""

from alembic import op
import sqlalchemy as sa


revision = "20260222"
down_revision = "20260218_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sales",
        sa.Column("advance_amount", sa.Numeric(10, 2), nullable=False, server_default="0"),
    )
    op.add_column(
        "sales",
        sa.Column("advance_payment_mode", sa.String(50), nullable=True),
    )
    op.add_column(
        "sales",
        sa.Column("advance_payment_date", sa.TIMESTAMP(), nullable=True),
    )
    op.add_column(
        "sales",
        sa.Column("balance_amount", sa.Numeric(10, 2), nullable=False, server_default="0"),
    )
    op.add_column(
        "sales",
        sa.Column("balance_payment_mode", sa.String(50), nullable=True),
    )
    op.add_column(
        "sales",
        sa.Column("balance_payment_date", sa.TIMESTAMP(), nullable=True),
    )
    op.add_column(
        "sales",
        sa.Column("payment_status", sa.String(50), nullable=False, server_default="pending"),
    )
    op.add_column(
        "sales",
        sa.Column("delivery_status", sa.String(50), nullable=False, server_default="pending"),
    )


def downgrade() -> None:
    op.drop_column("sales", "delivery_status")
    op.drop_column("sales", "payment_status")
    op.drop_column("sales", "balance_payment_date")
    op.drop_column("sales", "balance_payment_mode")
    op.drop_column("sales", "balance_amount")
    op.drop_column("sales", "advance_payment_date")
    op.drop_column("sales", "advance_payment_mode")
    op.drop_column("sales", "advance_amount")
