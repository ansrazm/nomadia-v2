import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, CheckConstraint, DateTime, Integer, String, Uuid, true
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Voucher(Base):
    __tablename__ = "vouchers"
    __table_args__ = (CheckConstraint("percent BETWEEN 1 AND 100", name="ck_vouchers_percent"),)

    code: Mapped[str] = mapped_column(String(32), primary_key=True)
    percent: Mapped[int] = mapped_column(Integer)
    active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())


class Quote(Base):
    """Log setiap penawaran harga yang dihitung (untuk audit/analitik)."""

    __tablename__ = "quotes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    subtotal: Mapped[int] = mapped_column(Integer)
    discount: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer)
    voucher: Mapped[str | None] = mapped_column(String(32), nullable=True)
    items: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
