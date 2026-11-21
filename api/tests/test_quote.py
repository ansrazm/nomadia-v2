from app.pricing import discount_amount
from .conftest import all_quotes


def test_discount_rounds_down():
    assert discount_amount(66001, 10) == 6600
    assert discount_amount(100, 100) == 100


async def test_quote_with_voucher_and_log(ctx):
    client, _, factory = ctx
    r = await client.post("/quote", json={"items": [{"sku": "jepang-esim-3", "qty": 2}, {"sku": "jepang-sim-7", "qty": 1}], "voucher": " nomad10 "})
    assert r.status_code == 200
    body = r.json()
    assert body["subtotal"] == 66000 * 2 + 165000
    assert body["discount"] == body["subtotal"] // 10
    assert body["total"] == body["subtotal"] - body["discount"]
    assert body["voucher"] == "NOMAD10"
    assert r.headers["x-request-id"] and "x-process-time-ms" in r.headers
    quotes = await all_quotes(factory)  # background task sudah jalan setelah respons
    assert len(quotes) == 1 and quotes[0].total == body["total"]


async def test_quote_without_voucher(ctx):
    client, _, _ = ctx
    r = await client.post("/quote", json={"items": [{"sku": "jepang-esim-3", "qty": 1}]})
    assert r.status_code == 200 and r.json()["discount"] == 0


async def test_unknown_product_404(ctx):
    client, _, _ = ctx
    r = await client.post("/quote", json={"items": [{"sku": "ngawur", "qty": 1}]})
    assert r.status_code == 404 and r.json()["detail"]["code"] == "PRODUCT_NOT_FOUND"


async def test_sold_out_409(ctx):
    client, _, _ = ctx
    r = await client.post("/quote", json={"items": [{"sku": "habis-1", "qty": 1}]})
    assert r.status_code == 409


async def test_inactive_or_unknown_voucher_404(ctx):
    client, _, _ = ctx
    for code in ("OFF", "TIDAKADA"):
        r = await client.post("/quote", json={"items": [{"sku": "jepang-esim-3", "qty": 1}], "voucher": code})
        assert r.status_code == 404 and r.json()["detail"]["code"] == "VOUCHER_INVALID"


async def test_validation_errors_422(ctx):
    client, _, _ = ctx
    assert (await client.post("/quote", json={"items": []})).status_code == 422
    assert (await client.post("/quote", json={"items": [{"sku": "a", "qty": 0}]})).status_code == 422
    dup = {"items": [{"sku": "a", "qty": 1}, {"sku": "a", "qty": 1}]}
    assert (await client.post("/quote", json=dup)).status_code == 422


async def test_strapi_down_502(ctx):
    client, strapi, _ = ctx
    strapi.fail = True
    r = await client.post("/quote", json={"items": [{"sku": "jepang-esim-3", "qty": 1}]})
    assert r.status_code == 502 and r.json()["detail"]["code"] == "CATALOG_UNAVAILABLE"
