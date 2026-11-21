from typing import Any

import httpx
from fastapi import Request


class StrapiUnavailable(Exception):
    pass


class StrapiClient:
    """Pembaca katalog dari Strapi: sumber kebenaran harga ada di CMS, bukan dari klien."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def products_by_sku(self, skus: list[str]) -> dict[str, dict[str, Any]]:
        params = {f"filters[sku][$in][{i}]": s for i, s in enumerate(skus)}
        params["pagination[pageSize]"] = str(len(skus))
        try:
            res = await self._client.get("/api/products", params=params)
            res.raise_for_status()
        except httpx.HTTPError as exc:
            raise StrapiUnavailable(str(exc)) from exc
        return {p["sku"]: p for p in res.json()["data"]}


def get_strapi(request: Request) -> StrapiClient:
    """Dependency: klien HTTP dibuat sekali di lifespan dan dipakai ulang."""
    return StrapiClient(request.app.state.http)
