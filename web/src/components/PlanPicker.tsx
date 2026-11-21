import { useMemo, useState } from "react";
import { rupiah } from "../lib/format";
import { typeHint, typeLabel, type Product, type ProductType } from "../lib/types";

const css = `
.pp{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:1rem}
.pp-hint{color:var(--muted);font-size:.9rem;margin:.6rem 0 1rem}
.pp-list{display:grid;gap:.5rem;margin:0 0 1rem;padding:0;list-style:none}
.pp-opt{display:flex;justify-content:space-between;gap:1rem;align-items:center;width:100%;text-align:left;font:inherit;color:inherit;background:var(--bg);border:2px solid var(--line);border-radius:10px;padding:.7rem .9rem;cursor:pointer}
.pp-opt[aria-checked="true"]{border-color:var(--brand)}
.pp-opt[aria-disabled="true"]{opacity:.5;cursor:not-allowed}
.pp-sub{color:var(--muted);font-size:.85rem}
.pp-price{font-weight:700;white-space:nowrap}
.pp-total{display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap}
.pp-big{font-size:1.4rem;font-weight:800}
`;

interface Props { destination: string; products: Product[]; whatsapp: string }

export default function PlanPicker({ destination, products, whatsapp }: Props) {
  const types = useMemo(() => [...new Set(products.map((p) => p.type))] as ProductType[], [products]);
  const [type, setType] = useState<ProductType>(types[0]);
  const plans = products.filter((p) => p.type === type);
  const [sku, setSku] = useState<string | undefined>(plans.find((p) => !p.soldOut)?.sku);
  const chosen = plans.find((p) => p.sku === sku);

  const pick = (t: ProductType) => {
    setType(t);
    setSku(products.find((p) => p.type === t && !p.soldOut)?.sku);
  };

  const message = chosen
    ? `Halo Nomadia, saya mau pesan ${chosen.name} (${chosen.data}, ${chosen.days} hari) seharga ${rupiah(chosen.price)}.`
    : "";
  const href = chosen && whatsapp ? `https://wa.me/${whatsapp}?text=${encodeURIComponent(message)}` : undefined;

  if (types.length === 0) return <p>Belum ada paket untuk {destination}.</p>;

  return (
    <div className="pp">
      <style>{css}</style>
      <div className="chips" role="tablist" aria-label="Jenis koneksi">
        {types.map((t) => (
          <button key={t} role="tab" className="chip" aria-pressed={t === type} aria-selected={t === type} onClick={() => pick(t)}>{typeLabel[t]}</button>
        ))}
      </div>
      <p className="pp-hint">{typeHint[type]}</p>

      <ul className="pp-list" role="radiogroup" aria-label={`Paket ${typeLabel[type]} ${destination}`}>
        {plans.map((p) => (
          <li key={p.sku}>
            <button
              type="button" role="radio" className="pp-opt"
              aria-checked={p.sku === sku} aria-disabled={p.soldOut}
              onClick={() => !p.soldOut && setSku(p.sku)}
            >
              <span>
                <strong>{p.days} hari · {p.data}</strong>
                <br /><span className="pp-sub">{p.soldOut ? "Stok kosong" : p.note}</span>
              </span>
              <span className="pp-price">{rupiah(p.price)}</span>
            </button>
          </li>
        ))}
      </ul>

      <div className="pp-total">
        <span className="pp-big">{chosen ? rupiah(chosen.price) : "—"}</span>
        <a className="btn" href={href} aria-disabled={!href} target="_blank" rel="noopener noreferrer">Pesan via WhatsApp</a>
      </div>
    </div>
  );
}
