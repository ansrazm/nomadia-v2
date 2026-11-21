# Nomadia Astro

Toko eSIM / SIM Card / Portable WiFi dengan **Astro** (web, static), **Strapi 5** (headless CMS) dan **FastAPI** (API harga/voucher), semuanya di PostgreSQL + Docker.
Model datanya diambil dari proyek Nomadia (12 destinasi, 89 paket).

```
cms/   Strapi 5: content type Destination + Product, akses baca publik otomatis, seed lewat REST
api/   FastAPI + SQLAlchemy async + Alembic: POST /quote (harga dari Strapi, voucher dari Postgres), pytest
web/   Astro: halaman statis dari Strapi, island React (filter destinasi, pemilih paket), SEO + sitemap
```

## Jalankan lokal

```bash
# 1) CMS + PostgreSQL
cp cms/.env.example cms/.env        # isi APP_KEYS, *_SALT, *_SECRET, ENCRYPTION_KEY dengan nilai acak
docker compose up --build           # admin: http://localhost:1337/admin (buat akun admin pertama)

# 2) Isi katalog: di admin buat API token "Full access" (Settings > API Tokens), lalu
cd cms && STRAPI_ADMIN_TOKEN=xxxx npm run seed

# 3) API (sudah ikut jalan di docker compose): http://localhost:8000/docs
#    tanpa Docker: cd api && pip install -r requirements-dev.txt && pytest -q

# 4) Web
cd ../web && cp .env.example .env && npm install && npm run dev   # http://localhost:4321
```

Tanpa CMS pun web tetap jalan: kosongkan `STRAPI_URL` dan web memakai `web/src/data/fixture.json`.

## Alur data

```
Editor ubah paket di Strapi ──webhook──▶ Vercel Deploy Hook ──▶ Astro build ulang (fetch Strapi) ──▶ situs statis
```

- Strapi admin > Settings > Webhooks: URL = Deploy Hook Vercel, event Entry create/update/delete.
- Environment variable di Vercel (project root `web/`): `STRAPI_URL`, `SITE_URL`, `PUBLIC_WHATSAPP_NUMBER`, opsional `STRAPI_TOKEN`.
- Host Strapi di VPS/Railway/Render dengan PostgreSQL dan volume untuk `public/uploads` (atau pakai provider upload S3/Cloudinary).

## Keputusan desain

- **Static output**: katalog jarang berubah, jadi build-time fetch cepat, murah, dan SEO-friendly. Kekurangannya, perubahan butuh rebuild (ditangani webhook).
- **Island architecture**: hanya `DestinationGrid` (`client:load`) dan `PlanPicker` (`client:visible`) yang memuat JS; sisanya HTML murni.
- **Content model**: `Destination 1..n Product` (relasi `oneToMany` / `manyToOne`), `draftAndPublish` dimatikan karena katalog langsung tayang.
- **Izin**: `src/index.js` (bootstrap) membuka `find`/`findOne` untuk role Public; tulis hanya lewat token/admin.
- **Gagal cepat**: build berhenti kalau Strapi mengembalikan 0 destinasi atau error, supaya situs kosong tidak ter-deploy.

## API harga (FastAPI)

`POST /quote` menerima `{items:[{sku, qty}], voucher?}` dan membaca harga **langsung dari Strapi** (klien tidak bisa mengirim harga sendiri).

| Kasus | Respons |
|---|---|
| sku tidak ada / voucher tidak berlaku | 404 `PRODUCT_NOT_FOUND` / `VOUCHER_INVALID` |
| paket sold out | 409 `SOLD_OUT` |
| input salah (qty 0, sku dobel, items kosong) | 422 (validasi Pydantic) |
| Strapi tidak terjangkau | 502 `CATALOG_UNAVAILABLE` |

Fitur FastAPI yang dipakai: async endpoint, dependency injection (`get_session`, `get_strapi`), validasi Pydantic v2, middleware (X-Request-ID, waktu proses), BackgroundTasks (log quote tidak menahan respons), lifespan (klien HTTP dipakai ulang), CORS, `/health` yang mengecek koneksi DB. Skema dikelola Alembic (`migrations/`), dijalankan otomatis saat container start.

Tes: 8 tes pytest (unit + endpoint, DB SQLite in-memory, Strapi diganti fake lewat `dependency_overrides`).

## Troubleshooting: API tidak tersedia setelah deploy

1. `docker compose ps` dan `docker compose logs api --tail 100`: container restart loop atau error migrasi?
2. `curl :8000/health`: 200 berarti app hidup; 5xx berarti koneksi DB bermasalah.
3. `DATABASE_URL` benar (host `api-db`, bukan `localhost`)? `docker compose exec api-db pg_isready`.
4. 502 `CATALOG_UNAVAILABLE` pada `/quote`: cek `STRAPI_URL` dan izin Public `find` di Strapi.
5. Rollback: deploy ulang image sebelumnya; migrasi Alembic bersifat maju, jadi migrasi baru harus kompatibel mundur.
