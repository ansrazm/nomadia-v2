import time
import uuid
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .config import get_settings
from .db import engine
from .routes import quote


@asynccontextmanager
async def lifespan(app: FastAPI):
    s = get_settings()
    headers = {"Authorization": f"Bearer {s.strapi_token}"} if s.strapi_token else {}
    app.state.http = httpx.AsyncClient(base_url=s.strapi_url, headers=headers, timeout=10)
    yield
    await app.state.http.aclose()
    await engine.dispose()


app = FastAPI(title="Nomadia Quote API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins.split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def request_meta(request: Request, call_next):
    """Middleware: beri setiap request ID dan catat durasinya di header respons."""
    rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    response.headers["X-Process-Time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response


@app.get("/health", tags=["ops"])
async def health():
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return {"status": "ok"}


app.include_router(quote.router)
