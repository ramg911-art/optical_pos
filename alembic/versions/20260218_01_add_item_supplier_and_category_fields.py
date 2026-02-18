"""add supplier and tax fields to items and description to categories

Revision ID: 20260218_01
Revises: 
Create Date: 2026-02-18
"""

from alembic import op
import sqlalchemy as sa


revision = "20260218_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Category metadata
    op.add_column(
        "categories",
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.add_column(
        "categories",
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.func.now(),
            nullable=True,
        ),
    )

    # Item supplier and tax fields
    op.add_column(
        "items",
        sa.Column("supplier_name", sa.String(length=200), nullable=True),
    )
    op.add_column(
        "items",
        sa.Column("supplier_gst", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "items",
        sa.Column("supplier_contact", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "items",
        sa.Column("supplier_address", sa.Text(), nullable=True),
    )
    op.add_column(
        "items",
        sa.Column("purchase_price", sa.Numeric(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("items", "purchase_price")
    op.drop_column("items", "supplier_address")
    op.drop_column("items", "supplier_contact")
    op.drop_column("items", "supplier_gst")
    op.drop_column("items", "supplier_name")

    op.drop_column("categories", "created_at")
    op.drop_column("categories", "description")

