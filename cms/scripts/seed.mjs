// Mengisi Strapi dengan katalog Nomadia (12 destinasi, 89 paket) lewat REST API. Aman dijalankan ulang (idempoten).
// Pakai: STRAPI_URL=http://localhost:1337 STRAPI_ADMIN_TOKEN=... npm run seed
import { readFile } from "node:fs/promises";

const BASE = (process.env.STRAPI_URL ?? "http://localhost:1337").replace(/\/+$/, "");
const TOKEN = process.env.STRAPI_ADMIN_TOKEN;
if (!TOKEN) throw new Error("Isi STRAPI_ADMIN_TOKEN (Settings > API Tokens > Full access).");

const headers = { "Content-Type": "application/json", Authorization: `Bearer ${TOKEN}` };
async function call(method, path, body) {
  const res = await fetch(`${BASE}/api${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined });
  const json = await res.json().catch(() => null);
  if (!res.ok) throw new Error(`${method} ${path} -> ${res.status} ${JSON.stringify(json?.error ?? json)}`);
  return json;
}
const q = (k, v) => `filters[${k}][$eq]=${encodeURIComponent(v)}`;

const catalog = JSON.parse(await readFile(new URL("./catalog.json", import.meta.url), "utf8"));
let created = 0, updated = 0;

for (const { products, ...dest } of catalog) {
  const found = (await call("GET", `/destinations?${q("slug", dest.slug)}`)).data[0];
  const d = found
    ? (updated++, (await call("PUT", `/destinations/${found.documentId}`, { data: dest })).data)
    : (created++, (await call("POST", "/destinations", { data: dest })).data);

  for (const p of products) {
    const existing = (await call("GET", `/products?${q("sku", p.sku)}`)).data[0];
    const data = { ...p, destination: { connect: [d.documentId] } };
    if (existing) { await call("PUT", `/products/${existing.documentId}`, { data }); updated++; }
    else { await call("POST", "/products", { data }); created++; }
  }
  console.log(`ok ${dest.slug} (${products.length} paket)`);
}
console.log(`Selesai: ${created} dibuat, ${updated} diperbarui.`);
