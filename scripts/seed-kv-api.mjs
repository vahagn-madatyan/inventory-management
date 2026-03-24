#!/usr/bin/env node
/**
 * Seed KV namespace via Cloudflare REST API.
 * Usage: CLOUDFLARE_API_TOKEN=xxx node scripts/seed-kv-api.mjs
 */

import { readFileSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ACCOUNT_ID =
  process.env.CLOUDFLARE_ACCOUNT_ID || "e4f07a390ec9f11df69062532e57a80f";
const NAMESPACE_ID =
  process.env.KV_NAMESPACE_ID || "686f63570a3241798376f261c68a564f";
const API_TOKEN = process.env.CLOUDFLARE_API_TOKEN;

if (!API_TOKEN) {
  console.error("ERROR: Set CLOUDFLARE_API_TOKEN environment variable");
  process.exit(1);
}

const DATA_DIR = join(__dirname, "..", "server", "data");

const files = {
  "data:inventory": "inventory.json",
  "data:orders": "orders.json",
  "data:demand_forecasts": "demand_forecasts.json",
  "data:backlog_items": "backlog_items.json",
  "data:spending": "spending.json",
  "data:transactions": "transactions.json",
  "data:purchase_orders": "purchase_orders.json",
  "data:restocking_orders": "restocking_orders.json",
};

const bulk = Object.entries(files).map(([key, file]) => ({
  key,
  value: readFileSync(join(DATA_DIR, file), "utf8"),
}));

console.log(`Uploading ${bulk.length} keys to KV namespace ${NAMESPACE_ID}...`);

const resp = await fetch(
  `https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/storage/kv/namespaces/${NAMESPACE_ID}/bulk`,
  {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${API_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(bulk),
  },
);

const result = await resp.json();
if (result.success) {
  console.log("KV seeding complete!");
} else {
  console.error("KV seeding failed:", JSON.stringify(result.errors, null, 2));
  process.exit(1);
}
