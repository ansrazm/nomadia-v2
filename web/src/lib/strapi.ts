import fixture from "../data/fixture.json";
import type { Destination, Product } from "./types";

const BASE = (import.meta.env.STRAPI_URL ?? "").replace(/\/+$/, "");
const TOKEN = import.meta.env.STRAPI_TOKEN as string | undefined;

// Bentuk respons Strapi 5 (REST): objek datar dengan documentId, tanpa pembungkus "attributes".
interface StrapiMedia { url: string }
interface StrapiProduct extends Product { documentId: string }
interface StrapiDestination {
  documentId: string; slug: string; name: string; code: string; region: string;
  network: string | null; position: number | null;
  thumb: StrapiMedia | null; banner: StrapiMedia | null;
  products?: StrapiProduct[];
}
interface Page<T> { data: T[]; meta: { pagination: { page: number; pageCount: number; total: number } } }

const abs = (m: StrapiMedia | null) => (m ? (m.url.startsWith("http") ? m.url : `${BASE}${m.url}`) : null);

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}/api${path}`, {
    headers: TOKEN ? { Authorization: `Bearer ${TOKEN}` } : {},
    signal: AbortSignal.timeout(15_000),
  });
  if (!res.ok) throw new Error(`Strapi ${path} -> HTTP ${res.status}`);
  return (await res.json()) as T;
}

let cache: Promise<Destination[]> | undefined;

/** Semua destinasi + paketnya, urut sesuai field position. Dipanggil beberapa kali saat build, tetapi hanya satu request. */
export function getDestinations(): Promise<Destination[]> {
  cache ??= load();
  return cache;
}

async function load(): Promise<Destination[]> {
  if (!BASE) {
    console.warn("[strapi] STRAPI_URL kosong: memakai src/data/fixture.json (hanya untuk development/CI).");
    return fixture as Destination[];
  }
  const qs = "populate[products]=true&populate[thumb]=true&populate[banner]=true&sort=position:asc&pagination[pageSize]=100";
  const { data } = await get<Page<StrapiDestination>>(`/destinations?${qs}`);
  if (data.length === 0) throw new Error("Strapi mengembalikan 0 destinasi: jalankan seed atau cek izin publik (find).");
  return data.map((d) => ({
    slug: d.slug, name: d.name, code: d.code, region: d.region, network: d.network, position: d.position ?? 0,
    thumbUrl: abs(d.thumb), bannerUrl: abs(d.banner),
    products: (d.products ?? [])
      .map(({ sku, type, name, days, data, price, note, soldOut }) => ({ sku, type, name, days, data, price, note, soldOut: !!soldOut }))
      .sort((a, b) => a.type.localeCompare(b.type) || a.days - b.days),
  }));
}

export async function getDestination(slug: string) {
  return (await getDestinations()).find((d) => d.slug === slug) ?? null;
}
