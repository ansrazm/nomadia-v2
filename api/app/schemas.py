from pydantic import BaseModel, Field, field_validator


class QuoteItemIn(BaseModel):
    sku: str = Field(min_length=1, max_length=80)
    qty: int = Field(ge=1, le=10)


class QuoteIn(BaseModel):
    items: list[QuoteItemIn] = Field(min_length=1, max_length=20)
    voucher: str | None = Field(default=None, max_length=32)

    @field_validator("voucher")
    @classmethod
    def normalize_voucher(cls, v: str | None) -> str | None:
        v = (v or "").strip().upper()
        return v or None

    @field_validator("items")
    @classmethod
    def unique_skus(cls, items: list[QuoteItemIn]) -> list[QuoteItemIn]:
        skus = [i.sku for i in items]
        if len(set(skus)) != len(skus):
            raise ValueError("sku duplikat: gabungkan lewat qty")
        return items


class QuoteLine(BaseModel):
    sku: str
    name: str
    qty: int
    unit_price: int
    line_total: int


class QuoteOut(BaseModel):
    id: str
    lines: list[QuoteLine]
    subtotal: int
    discount: int
    total: int
    voucher: str | None
