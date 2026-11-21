export const rupiah = (n: number) => "Rp " + n.toLocaleString("id-ID");
export const flagUrl = (code: string) => `https://flagcdn.com/w80/${code}.png`;

/** Harga mulai dari = paket termurah yang masih bisa dibeli; null bila belum ada. */
export const startingPrice = (products: { price: number; soldOut: boolean }[]) => {
  const prices = products.filter((p) => !p.soldOut).map((p) => p.price);
  return prices.length ? Math.min(...prices) : null;
};
