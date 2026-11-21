export type ProductType = "esim" | "sim" | "wifi";

export interface Product {
  sku: string;
  type: ProductType;
  name: string;
  days: number;
  data: string;
  price: number;
  note: string | null;
  soldOut: boolean;
}

export interface Destination {
  slug: string;
  name: string;
  code: string;
  region: string;
  network: string | null;
  position: number;
  thumbUrl: string | null;
  bannerUrl: string | null;
  products: Product[];
}

export const typeLabel: Record<ProductType, string> = { esim: "eSIM", sim: "SIM Card", wifi: "Portable WiFi" };
export const typeHint: Record<ProductType, string> = {
  esim: "Aktif lewat QR, tanpa kartu fisik",
  sim: "Kartu fisik untuk ponsel tanpa eSIM",
  wifi: "Satu alat untuk hingga 5 perangkat",
};
