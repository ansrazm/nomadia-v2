import { useMemo, useState } from "react";
import { flagUrl, rupiah } from "../lib/format";
import { typeLabel, type ProductType } from "../lib/types";

export interface CardData {
  slug: string; name: string; code: string; region: string; network: string | null;
  thumbUrl: string | null; startingPrice: number | null; types: ProductType[];
}

const css = `
.dg-tools{display:flex;flex-wrap:wrap;gap:.75rem;align-items:center;margin:1rem 0 1.25rem}
.dg-search{flex:1 1 220px;padding:.6rem .8rem;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink);font:inherit}
.dg-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:1rem;list-style:none;padding:0;margin:0}
.dg-card{display:block;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;text-decoration:none;color:inherit;height:100%;transition:transform .15s,box-shadow .15s}
.dg-card:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,.08)}
.dg-img{aspect-ratio:16/9;width:100%;object-fit:cover;background:var(--line);display:block}
.dg-body{padding:.8rem .9rem 1rem}
.dg-name{font-weight:700;margin:0}
.dg-meta{color:var(--muted);font-size:.85rem;margin:.15rem 0 .5rem}
.dg-price{font-weight:700;color:var(--brand)}
.dg-empty{color:var(--muted);padding:2rem 0;text-align:center}
`;

export default function DestinationGrid({ items }: { items: CardData[] }) {
  const [query, setQuery] = useState("");
  const [type, setType] = useState<ProductType | null>(null);

  const shown = useMemo(() => {
    const q = query.trim().toLowerCase();
    return items.filter(
      (d) => (!type || d.types.includes(type)) && (!q || d.name.toLowerCase().includes(q) || d.region.toLowerCase().includes(q)),
    );
  }, [items, query, type]);

  return (
    <section aria-label="Daftar destinasi">
      <style>{css}</style>
      <div className="dg-tools">
        <input className="dg-search" type="search" placeholder="Cari negara atau kawasan…" value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Cari destinasi" />
        <div className="chips" role="group" aria-label="Filter jenis koneksi">
          <button className="chip" aria-pressed={type === null} onClick={() => setType(null)}>Semua</button>
          {(Object.keys(typeLabel) as ProductType[]).map((t) => (
            <button key={t} className="chip" aria-pressed={type === t} onClick={() => setType(type === t ? null : t)}>{typeLabel[t]}</button>
          ))}
        </div>
      </div>

      {shown.length === 0 ? (
        <p className="dg-empty">Tidak ada destinasi yang cocok.</p>
      ) : (
        <ul className="dg-grid">
          {shown.map((d) => (
            <li key={d.slug}>
              <a className="dg-card" href={`/destinasi/${d.slug}`}>
                <img className="dg-img" src={d.thumbUrl ?? flagUrl(d.code)} alt={`Bendera ${d.name}`} loading="lazy" />
                <div className="dg-body">
                  <h3 className="dg-name">{d.name}</h3>
                  <p className="dg-meta">{d.region}{d.network ? ` · ${d.network}` : ""}</p>
                  <span className="dg-price">{d.startingPrice ? `Mulai ${rupiah(d.startingPrice)}` : "Belum tersedia"}</span>
                </div>
              </a>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
