# Restocking Tab Implementation Plan

## Context

The inventory management app (Vue 3 + FastAPI) needs a new Restocking tab that combines demand forecast data with low-stock inventory items, lets users set a budget, select items to restock, and submit orders that appear in the existing Orders tab.

## Files to Modify/Create

### 1. Backend Data: `server/data/demand_forecasts.json`

Add `unit_cost` field to each forecast item. Since most forecast SKUs (WDG-001, BRG-102, etc.) don't exist in inventory, costs are assigned directly:

- WDG-001: $24.99, BRG-102: $89.50, GSK-203: $12.75, MTR-304: $445.00
- FLT-405: $8.25, VLV-506: $156.00, PSU-501: $18.99, SNR-420: $89.50, CTL-330: $32.75

### 2. New File: `server/data/restocking_orders.json`

Empty array `[]` — persistence file for submitted orders.

### 3. Backend: `server/mock_data.py`

Add: `restocking_orders = load_json_file('restocking_orders.json')`

### 4. Backend: `server/main.py`

**New Pydantic models:**

- `RestockingOrderItem` (sku, name, quantity, unit_cost, line_total, source)
- `RestockingOrder` (id, order_date, items, total_cost, budget, status, expected_delivery)
- `CreateRestockingOrderRequest` (items, total_cost, budget)

**New endpoints:**

- `GET /api/restocking/recommendations` — Merges two data sources:
  - **Demand forecast items** where `forecasted_demand > current_demand`: qty = gap (`forecasted - current`)
  - **Inventory items** where `quantity_on_hand <= reorder_point`: qty = `reorder_point - quantity_on_hand + ceil(reorder_point * 0.2)`
  - Deduplicates by SKU (keeps higher quantity), tags source as "demand"/"low_stock"/"both"
  - Sorts: "both" first, then low_stock (by deficit desc), then demand (by gap desc)
- `POST /api/restocking-orders` — Creates order with auto-generated ID (`RST-2025-NNNN`), computes `expected_delivery` based on max item cost (>=$200: 14 days, >=$50: 10 days, else 7 days), status="Submitted"
- `GET /api/restocking-orders` — Returns all submitted orders

### 5. Frontend API: `client/src/api.js`

Add 3 methods: `getRestockingRecommendations()`, `getRestockingOrders()`, `submitRestockingOrder(data)`

### 6. New File: `client/src/views/Restocking.vue`

**Layout (top to bottom):**

1. Page header (title + description)
2. Budget control card — range slider ($0-$50,000, step $500, default $10,000) + numeric input
3. Stats grid — 4 cards: Recommended Items count, Selected Items count, Estimated Cost, Budget Remaining
4. Recommendations table — checkbox, name, SKU, source badge, editable quantity input, unit cost, line total
5. Budget progress bar (green/yellow/red based on spend ratio)
6. Footer — running total vs budget, "Place Order" button (disabled if over budget or nothing selected)
7. Success message after submission with order number and expected delivery

**Reactive state:** budget ref, recommendations ref, selectedItems map `{ sku: { selected, quantity } }`, loading/error/submitting/submitted refs. Computed: selectedList, runningTotal, budgetRemaining, isOverBudget, canSubmit.

**On load:** fetch recommendations, auto-select all items with default quantities. User can toggle items and adjust quantities. Budget slider reactively updates which items fit.

### 7. Router: `client/src/main.js`

Add import and route: `{ path: '/restocking', component: Restocking }`

### 8. Navigation: `client/src/App.vue`

Add `<router-link to="/restocking">` in nav-tabs between Demand Forecast and Reports.

### 9. i18n: `client/src/locales/en.js` and `ja.js`

Add `nav.restocking` ("Restocking" / "補充") and full `restocking: { ... }` section with all UI strings.

### 10. Orders Tab: `client/src/views/Orders.vue`

Add a "Submitted Restocking Orders" section below the existing orders table:

- Fetches from `api.getRestockingOrders()` on mount
- Table columns: Order ID, Date, Items (expandable), Total Cost, Status badge, Expected Delivery
- Only shows section if there are restocking orders (`v-if="restockingOrders.length > 0"`)

## Key Design Decisions

- **Recommendation algorithm**: Demand gap items + low-stock items, deduplicated by SKU
- **Budget slider**: $0-$50K, step $500, default $10K
- **Lead time**: Calculated server-side from max item cost (7/10/14 days)
- **Persistence**: In-memory list on backend (matches existing app pattern — resets on server restart)
- **Currency**: Uses existing `formatCurrency` from `utils/currency.js` for USD/JPY support

## Verification

1. Start backend (`cd server && uv run python main.py`), confirm `GET /api/restocking/recommendations` returns merged list
2. Start frontend (`cd client && npm run dev`), navigate to Restocking tab
3. Adjust budget slider — verify items table and totals update reactively
4. Toggle items and change quantities — verify running total recalculates
5. Submit an order — verify success message with order ID and delivery date
6. Navigate to Orders tab — verify "Submitted Restocking Orders" section shows the order
7. Test i18n by switching to Japanese
