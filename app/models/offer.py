from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Offer(Base):
    __tablename__ = "offers"
    __table_args__ = (UniqueConstraint("store_id", "external_id", name="uq_offer_store_external"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"), nullable=True, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), index=True)
    external_id: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(500))
    normalized_title: Mapped[str] = mapped_column(String(500), index=True)
    current_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    pix_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    installment_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    shipping_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    total_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    availability: Mapped[str] = mapped_column(String(80), default="unknown")
    url: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    coupon_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    discount_percent: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    match_score: Mapped[int] = mapped_column(Integer, default=0)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="offers")
    store = relationship("Store", back_populates="offers")

