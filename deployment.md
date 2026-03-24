# Deploy Inventory Management App to Cloudflare

## Context

The inventory management system (Vue 3 frontend + Python FastAPI backend) currently runs locally only. The goal is to deploy the full stack to Cloudflare infrastructure: the frontend to Cloudflare Pages, the backend as a Cloudflare Python Worker with KV for data storage, and GitHub Actions for CI/CD. The Cloudflare MCP tools will be used to provision resources.

**Target account:** CNO Lab (`e4f07a390ec9f11df69062532e57a80f`)

---

## Architecture

```
                    ┌──────────────────────┐
                    │   GitHub Actions      │
                    │   (CI/CD Pipeline)    │
                    └────┬────────────┬─────┘
                         │            │
                    deploy           deploy
                         │            │
              ┌──────────▼──┐   ┌────▼──────────────┐
              │  Cloudflare  │   │  Cloudflare Python │
              │  Pages       │   │  Worker            │
              │  (Vue SPA)   │──▶│  (FastAPI adapted) │
              │  *.pages.dev │   │  *.workers.dev     │
              └──────────────┘   └────────┬───────────┘
                                          │
                                    ┌─────▼──────┐
                                    │ Cloudflare  │
                                    │ KV          │
                                    │ (JSON data) │
                                    └─────────────┘
```

---

## Step 1: Provision Cloudflare Resources via MCP

Use Cloudflare MCP tools to create the KV namespace:

1. Set active account to CNO Lab
2. Create KV namespace `inventory-data` via `mcp__plugin_cloudflare_cloudflare-bindings__kv_namespace_create`
3. Note the returned namespace ID for use in wrangler config and GitHub secrets

Pages project and Worker are auto-created on first `wrangler deploy`.

---

## Step 2: Create the Python Worker (Backend)

### New directory: `worker/`

**`worker/wrangler.jsonc`** — Worker configuration:
```jsonc
{
  "name": "inventory-api",
  "main": "src/entry.py",
  "compatibility_date": "2026-03-24",
  "kv_namespaces": [
    { "binding": "INVENTORY_KV", "id": "<KV_NAMESPACE_ID>" }
  ]
}
```

**`worker/pyproject.toml`** — Python dependencies:
- fastapi, pydantic (both confirmed supported on Python Workers via Pyodide)

**`worker/src/entry.py`** — WorkerEntrypoint class:
- Receives `fetch(self, request)` calls
- Bridges to FastAPI app via ASGI/TestClient pattern
- Adds CORS headers to all responses (`Access-Control-Allow-Origin: *`)
- Handles OPTIONS preflight requests

**`worker/src/app.py`** — FastAPI app factory (adapted from `server/main.py`):
- `create_app(env)` factory function that accepts Worker env with KV binding
- All 21 endpoints ported from `server/main.py` — same Pydantic models, same filter logic
- Data loaded from KV instead of file system (async `load_data_from_kv()`)
- CORS middleware configured

**`worker/src/mock_data.py`** — KV data loader:
- `async load_data_from_kv(kv)` reads 8 keys from KV (`data:inventory`, `data:orders`, etc.)
- Returns dict with all datasets
- POST endpoints (restocking orders, tasks) write back to KV for persistence

### Fallback plan
If FastAPI doesn't work cleanly on Pyodide, fall back to a lightweight direct URL router in `entry.py` that reuses the pure Python filter logic without the FastAPI framework. The filtering code is simple list comprehensions that will work anywhere.

---

## Step 3: KV Data Seeding

### New file: `scripts/seed-kv.sh`

Upload each JSON file to KV with `data:` prefix keys:

| KV Key | Source File |
|--------|------------|
| `data:inventory` | `server/data/inventory.json` |
| `data:orders` | `server/data/orders.json` |
| `data:demand_forecasts` | `server/data/demand_forecasts.json` |
| `data:backlog_items` | `server/data/backlog_items.json` |
| `data:spending` | `server/data/spending.json` |
| `data:transactions` | `server/data/transactions.json` |
| `data:purchase_orders` | `server/data/purchase_orders.json` |
| `data:restocking_orders` | `server/data/restocking_orders.json` |

Uses `npx wrangler kv key put "data:<name>" --path=server/data/<name>.json --namespace-id=<ID>` for each file.

---

## Step 4: Modify Frontend for Configurable API URL

### Modify: `client/src/api.js` (line 3)
```js
// Before:
const API_BASE_URL = 'http://localhost:8001/api'
// After:
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api'
```

### Modify: `client/src/views/Reports.vue` (lines 156, 162)
Replace hardcoded `http://localhost:8001/api/reports/*` URLs with `api.js` methods or the same env variable pattern.

### New: `client/.env.development`
```
VITE_API_URL=http://localhost:8001/api
```

### New: `client/.env.production`
```
VITE_API_URL=https://inventory-api.<subdomain>.workers.dev/api
```

The `VITE_` prefix ensures Vite bakes the value into the bundle at build time.

---

## Step 5: Configure Pages Deployment for Vue SPA

The frontend deploys to Cloudflare Pages via `wrangler pages deploy client/dist`.

### SPA routing
Create `client/public/_redirects`:
```
/* /index.html 200
```

This ensures vue-router history mode works (all paths serve `index.html`). If Pages doesn't support 200 rewrites, we'll use Workers Static Assets with `not_found_handling: "single-page-application"` as fallback.

---

## Step 6: GitHub Actions CI/CD

### New: `.github/workflows/deploy.yml`

```yaml
name: Deploy to Cloudflare
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install fastapi uvicorn pydantic pytest httpx pytest-cov
      - run: cd tests && pytest backend/ -v

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          workingDirectory: worker
          command: deploy

  seed-kv:
    needs: deploy-backend
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: kv bulk put scripts/kv-bulk.json --namespace-id=${{ secrets.KV_NAMESPACE_ID }}

  deploy-frontend:
    needs: deploy-backend
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: cd client && npm install && npm run build
        env:
          VITE_API_URL: https://inventory-api.${{ secrets.CF_SUBDOMAIN }}.workers.dev/api
      - uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: pages deploy client/dist --project-name=inventory-mgmt
```

### Required GitHub Secrets
| Secret | Value |
|--------|-------|
| `CLOUDFLARE_API_TOKEN` | API token with Workers + Pages + KV edit permissions |
| `CLOUDFLARE_ACCOUNT_ID` | `e4f07a390ec9f11df69062532e57a80f` |
| `KV_NAMESPACE_ID` | From Step 1 |
| `CF_SUBDOMAIN` | Account workers.dev subdomain |

---

## Step 7: Update .gitignore

Add:
```
worker/.wrangler/
client/.env.local
.dev.vars
```

---

## File Change Summary

### New files (10)
| File | Purpose |
|------|---------|
| `worker/wrangler.jsonc` | Worker config with KV binding |
| `worker/pyproject.toml` | Python Worker dependencies |
| `worker/src/entry.py` | WorkerEntrypoint → FastAPI bridge |
| `worker/src/app.py` | FastAPI app factory (adapted from server/main.py) |
| `worker/src/mock_data.py` | KV-based data loader |
| `scripts/seed-kv.sh` | KV data seeding script |
| `.github/workflows/deploy.yml` | CI/CD pipeline |
| `client/.env.development` | Local dev API URL |
| `client/.env.production` | Production API URL |
| `client/public/_redirects` | SPA routing for Pages |

### Modified files (3)
| File | Change |
|------|--------|
| `client/src/api.js` | Line 3: use `import.meta.env.VITE_API_URL` with localhost fallback |
| `client/src/views/Reports.vue` | Lines 156, 162: replace hardcoded localhost URLs |
| `.gitignore` | Add worker/.wrangler/, .dev.vars |

### Unchanged (everything else)
- `server/` directory stays as-is for local development
- `tests/` stay as-is — they test against `server/main.py` locally
- All other Vue files unchanged

---

## Implementation Order

1. Provision KV namespace via MCP
2. Create `worker/` directory with all files
3. Seed KV data
4. Test worker locally with `npx wrangler dev` (in worker/ dir)
5. Modify frontend API URL configuration
6. Test frontend build
7. Create GitHub Actions workflow
8. Deploy and verify end-to-end

---

## Verification

1. **Local backend**: `cd server && uv run python main.py` still works
2. **Local worker**: `cd worker && npx wrangler dev` serves API on localhost
3. **Local frontend**: `cd client && npm run dev` connects to local backend
4. **Deployed worker**: `curl https://inventory-api.*.workers.dev/api/inventory` returns JSON
5. **Deployed frontend**: Visit `https://inventory-mgmt.pages.dev`, all views load data
6. **CORS**: Browser console shows no CORS errors
7. **CI/CD**: Push to main triggers test → deploy pipeline
8. **Existing tests**: `cd tests && pytest backend/ -v` — all 51 tests pass
