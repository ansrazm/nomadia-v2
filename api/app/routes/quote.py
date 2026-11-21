import logging
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import SessionLocal, get_session
from ..models import Quote, Voucher
from ..pricing import discount_amount
from ..schemas import QuoteIn, QuoteLine, QuoteOut
from ..strapi import StrapiClient, StrapiUnavailable, get_strapi

log = logging.getLogger("nomadia.quote")
router = APIRouter(tags=["quote"])


async def save_quote(session_factory, quote: Quote) -> None:
    """Background task: gagal menyimpan log tidak boleh menggagalkan respons ke pelanggan."""
    try:
        async with session_factory() as session:
            session.add(quote)
            await session.commit()
    except Exception:  # noqa: BLE001
        log.exception("gagal menyimpan quote %s", quote.id)


def get_session_factory():
    return SessionLocal


@router.post("/quote", response_model=QuoteOut)
async def create_quote(
    body: QuoteIn,
    background: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    strapi: StrapiClient = Depends(get_strapi),
    session_factory=Depends(get_session_factory),
) -> QuoteOut:
    try:
        catalog = await strapi.products_by_sku([i.sku for i in body.items])
    except StrapiUnavailable:
        raise HTTPException(502, detail={"code": "CATALOG_UNAVAILABLE", "message": "Katalog sedang tidak bisa dibaca."})

    lines: list[QuoteLine] = []
    for item in body.items:
        product = catalog.get(item.sku)
        if product is None:
            raise HTTPException(404, detail={"code": "PRODUCT_NOT_FOUND", "message": f"Paket {item.sku} tidak ada."})
        if product.get("soldOut"):
            raise HTTPException(409, detail={"code": "SOLD_OUT", "message": f"{product['name']} sedang kosong."})
        price = int(product["price"])
        lines.append(QuoteLine(sku=item.sku, name=product["name"], qty=item.qty, unit_price=price, line_total=price * item.qty))

    subtotal = sum(line.line_total for line in lines)
    discount = 0
    if body.voucher:
        voucher = await session.get(Voucher, body.voucher)
        if voucher is None or not voucher.active:
            raise HTTPException(404, detail={"code": "VOUCHER_INVALID", "message": "Kode voucher tidak berlaku."})
        discount = discount_amount(subtotal, voucher.percent)

    quote = Quote(
        id=uuid.uuid4(), subtotal=subtotal, discount=discount, total=subtotal - discount, voucher=body.voucher,
        items=[{"sku": l.sku, "qty": l.qty, "unit_price": l.unit_price} for l in lines],
    )
    background.add_task(save_quote, session_factory, quote)
    return QuoteOut(id=str(quote.id), lines=lines, subtotal=subtotal, discount=discount, total=quote.total, voucher=body.voucher)
