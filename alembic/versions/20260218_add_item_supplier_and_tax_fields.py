"""Add supplier and tax fields to items

Revision ID: add_item_supplier_and_tax_fields
Revises: 
Create Date: 2026-02-18
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_item_supplier_and_tax_fields"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("items", sa.Column("purchase_price", sa.Numeric(), nullable=True))
    op.add_column(
        "items",
        sa.Column(
            "supplier_name",
            sa.String(length=200),
            nullable=False,
            server_default="",
        ),
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


def downgrade() -> None:
    op.drop_column("items", "supplier_address")
    op.drop_column("items", "supplier_contact")
    op.drop_column("items", "supplier_gst")
    op.drop_column("items", "supplier_name")
    op.drop_column("items", "purchase_price")

