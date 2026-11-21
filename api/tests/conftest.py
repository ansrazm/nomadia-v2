import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db import get_session
from app.main import app
from app.models import Base, Quote, Voucher
from app.routes.quote import get_session_factory
from app.strapi import get_strapi

CATALOG = {
    "jepang-esim-3": {"sku": "jepang-esim-3", "name": "eSIM Jepang 3 hari", "price": 66000, "soldOut": False},
    "jepang-sim-7": {"sku": "jepang-sim-7", "name": "SIM Card Jepang 7 hari", "price": 165000, "soldOut": False},
    "habis-1": {"sku": "habis-1", "name": "Paket habis", "price": 10000, "soldOut": True},
}


class FakeStrapi:
    fail = False

    async def products_by_sku(self, skus):
        from app.strapi import StrapiUnavailable

        if self.fail:
            raise StrapiUnavailable("down")
        return {s: CATALOG[s] for s in skus if s in CATALOG}


@pytest_asyncio.fixture
async def ctx():
    engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        s.add_all([Voucher(code="NOMAD10", percent=10, active=True), Voucher(code="OFF", percent=50, active=False)])
        await s.commit()

    async def _session():
        async with factory() as s:
            yield s

    strapi = FakeStrapi()
    app.dependency_overrides[get_session] = _session
    app.dependency_overrides[get_strapi] = lambda: strapi
    app.dependency_overrides[get_session_factory] = lambda: factory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client, strapi, factory
    app.dependency_overrides.clear()
    await engine.dispose()


async def all_quotes(factory):
    async with factory() as s:
        return (await s.execute(select(Quote))).scalars().all()
