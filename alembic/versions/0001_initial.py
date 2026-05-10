"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "stores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("base_url", sa.String(length=300), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_stores_slug"), "stores", ["slug"], unique=True)
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("query", sa.String(length=255), nullable=False),
        sa.Column("normalized_query", sa.String(length=255), nullable=False),
        sa.Column("sku", sa.String(length=120), nullable=True),
        sa.Column("brand", sa.String(length=120), nullable=True),
        sa.Column("model", sa.String(length=160), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_normalized_query"), "products", ["normalized_query"], unique=False)
    op.create_index(op.f("ix_products_query"), "products", ["query"], unique=False)
    op.create_index(op.f("ix_products_sku"), "products", ["sku"], unique=False)
    op.create_table(
        "offers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("store_id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("normalized_title", sa.String(length=500), nullable=False),
        sa.Column("current_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("pix_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("installment_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("shipping_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("total_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("availability", sa.String(length=80), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("coupon_code", sa.String(length=120), nullable=True),
        sa.Column("discount_percent", sa.Numeric(6, 2), nullable=True),
        sa.Column("match_score", sa.Integer(), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("store_id", "external_id", name="uq_offer_store_external"),
    )
    op.create_index(op.f("ix_offers_external_id"), "offers", ["external_id"], unique=False)
    op.create_index(op.f("ix_offers_normalized_title"), "offers", ["normalized_title"], unique=False)
    op.create_index(op.f("ix_offers_product_id"), "offers", ["product_id"], unique=False)
    op.create_index(op.f("ix_offers_store_id"), "offers", ["store_id"], unique=False)
    op.create_table(
        "price_alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("target_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("store_slug", sa.String(length=80), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("telegram_chat_id", sa.String(length=80), nullable=True),
        sa.Column("frequency_minutes", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_price_alerts_enabled"), "price_alerts", ["enabled"], unique=False)
    op.create_index(op.f("ix_price_alerts_product_id"), "price_alerts", ["product_id"], unique=False)
    op.create_index(op.f("ix_price_alerts_store_slug"), "price_alerts", ["store_slug"], unique=False)
    op.create_table(
        "price_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("offer_id", sa.Integer(), nullable=True),
        sa.Column("store_slug", sa.String(length=80), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("pix_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("shipping_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("total_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["offer_id"], ["offers.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_price_history_collected_at"), "price_history", ["collected_at"], unique=False)
    op.create_index(op.f("ix_price_history_product_id"), "price_history", ["product_id"], unique=False)
    op.create_index(op.f("ix_price_history_store_slug"), "price_history", ["store_slug"], unique=False)


def downgrade() -> None:
    op.drop_table("price_history")
    op.drop_table("price_alerts")
    op.drop_table("offers")
    op.drop_table("products")
    op.drop_table("stores")

