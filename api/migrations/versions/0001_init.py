"""vouchers + quotes

Revision ID: 0001
Revises:
"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None


def upgrade() -> None:
    vouchers = op.create_table(
        "vouchers",
        sa.Column("code", sa.String(32), primary_key=True),
        sa.Column("percent", sa.Integer, nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.CheckConstraint("percent BETWEEN 1 AND 100", name="ck_vouchers_percent"),
    )
    op.create_table(
        "quotes",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column("subtotal", sa.Integer, nullable=False),
        sa.Column("discount", sa.Integer, nullable=False),
        sa.Column("total", sa.Integer, nullable=False),
        sa.Column("voucher", sa.String(32), nullable=True),
        sa.Column("items", sa.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_quotes_created_at", "quotes", ["created_at"])
    op.bulk_insert(vouchers, [{"code": "NOMAD10", "percent": 10, "active": True}])


def downgrade() -> None:
    op.drop_index("ix_quotes_created_at", table_name="quotes")
    op.drop_table("quotes")
    op.drop_table("vouchers")
