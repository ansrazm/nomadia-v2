"use strict";

// Katalog bersifat publik (hanya baca). Tulis butuh API token / login admin.
const PUBLIC_READ = [
  "api::destination.destination.find",
  "api::destination.destination.findOne",
  "api::product.product.find",
  "api::product.product.findOne",
];

module.exports = {
  register() {},
  async bootstrap({ strapi }) {
    const role = await strapi.db.query("plugin::users-permissions.role").findOne({ where: { type: "public" } });
    if (!role) return;
    for (const action of PUBLIC_READ) {
      const exists = await strapi.db.query("plugin::users-permissions.permission").findOne({ where: { action, role: role.id } });
      if (!exists) await strapi.db.query("plugin::users-permissions.permission").create({ data: { action, role: role.id } });
    }
  },
};
