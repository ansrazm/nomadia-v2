import { defineConfig } from "astro/config";
import react from "@astrojs/react";
import sitemap from "@astrojs/sitemap";

// Static output: halaman dibangun dari Strapi saat build, lalu disajikan sebagai file statis (Vercel/Netlify/Cloudflare).
// Konten berubah di Strapi -> webhook -> deploy hook -> build ulang (lihat README).
export default defineConfig({
  site: process.env.SITE_URL || "http://localhost:4321",
  integrations: [react(), sitemap()],
});
