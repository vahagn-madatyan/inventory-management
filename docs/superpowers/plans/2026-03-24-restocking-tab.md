# Restocking Tab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new Restocking tab that merges demand forecasts with low-stock inventory, lets users set a budget, select items, and submit restocking orders that appear in the Orders tab.

**Architecture:** Backend provides a recommendations endpoint merging demand gap + low-stock data, a POST endpoint for order submission, and a GET for listing orders. Frontend adds a new Restocking.vue with budget slider, item selection table, and order flow. Submitted orders appear in the Orders tab.

**Tech Stack:** Vue 3 Composition API, FastAPI, Pydantic, in-memory storage, existing i18n/currency utilities.

---

## File Map

| Action | Path                                 | Responsibility                                                     |
| ------ | ------------------------------------ | ------------------------------------------------------------------ |
| Modify | `server/data/demand_forecasts.json`  | Add `unit_cost` to each forecast item                              |
| Create | `server/data/restocking_orders.json` | Empty persistence file for submitted orders                        |
| Modify | `server/mock_data.py`                | Load restocking_orders                                             |
| Modify | `server/main.py`                     | New models + 3 endpoints (recommendations, POST order, GET orders) |
| Modify | `client/src/api.js`                  | 3 new API methods                                                  |
| Create | `client/src/views/Restocking.vue`    | Full restocking tab UI                                             |
| Modify | `client/src/main.js`                 | Add route                                                          |
| Modify | `client/src/App.vue`                 | Add nav link                                                       |
| Modify | `client/src/locales/en.js`           | English i18n strings                                               |
| Modify | `client/src/locales/ja.js`           | Japanese i18n strings                                              |
| Modify | `client/src/views/Orders.vue`        | Show submitted restocking orders section                           |
| Create | `tests/backend/test_restocking.py`   | Tests for all 3 new endpoints                                      |

---

### Task 1: Add `unit_cost` to demand forecasts data

**Files:**

- Modify: `server/data/demand_forecasts.json`

- [ ] **Step 1: Add unit_cost field to each forecast item**

Add `unit_cost` to each item per the spec (RESTOCK-PLAN.md section 1):

```json
{"id": "1", "item_sku": "WDG-001", ..., "unit_cost": 24.99}
{"id": "2", "item_sku": "BRG-102", ..., "unit_cost": 89.50}
{"id": "3", "item_sku": "GSK-203", ..., "unit_cost": 12.75}
{"id": "4", "item_sku": "MTR-304", ..., "unit_cost": 445.00}
{"id": "5", "item_sku": "FLT-405", ..., "unit_cost": 8.25}
{"id": "6", "item_sku": "VLV-506", ..., "unit_cost": 156.00}
{"id": "7", "item_sku": "PSU-501", ..., "unit_cost": 18.99}
{"id": "8", "item_sku": "SNR-420", ..., "unit_cost": 89.50}
{"id": "9", "item_sku": "CTL-330", ..., "unit_cost": 32.75}
```

Note: These costs differ from `inventory.json` `unit_cost` values. The demand forecast `unit_cost` represents the restocking/procurement cost for these specific items, which may differ from the general inventory purchase cost.

- [ ] **Step 2: Update DemandForecast Pydantic model in `server/main.py`**

Add `unit_cost: Optional[float] = None` to the `DemandForecast` model.

- [ ] **Step 3: Commit**

```bash
git add server/data/demand_forecasts.json server/main.py
git commit -m "feat: add unit_cost to demand forecast data"
```

---

### Task 2: Backend data + models for restocking orders

**Files:**

- Create: `server/data/restocking_orders.json`
- Modify: `server/mock_data.py`
- Modify: `server/main.py`

- [ ] **Step 1: Create empty restocking_orders.json**

```json
[]
```

- [ ] **Step 2: Load restocking_orders in mock_data.py**

Add after the `purchase_orders` line:

```python
restocking_orders = load_json_file('restocking_orders.json')
```

- [ ] **Step 3: Add import of restocking_orders in main.py**

Update the import line:

```python
from mock_data import inventory_items, orders, demand_forecasts, backlog_items, spending_summary, monthly_spending, category_spending, recent_transactions, purchase_orders, restocking_orders
```

- [ ] **Step 4: Add Pydantic models in main.py**

Add after `CreatePurchaseOrderRequest`:

```python
class RestockingOrderItem(BaseModel):
    sku: str
    name: str
    quantity: int
    unit_cost: float
    line_total: float
    source: str

class RestockingOrder(BaseModel):
    id: str
    order_date: str
    items: List[RestockingOrderItem]
    total_cost: float
    budget: float
    status: str
    expected_delivery: str

class CreateRestockingOrderRequest(BaseModel):
    items: List[RestockingOrderItem]
    total_cost: float
    budget: float
```

- [ ] **Step 5: Commit**

```bash
git add server/data/restocking_orders.json server/mock_data.py server/main.py
git commit -m "feat: add restocking order data model and persistence"
```

---

### Task 3: Backend restocking recommendations endpoint

**Files:**

- Modify: `server/main.py`
- Create: `tests/backend/test_restocking.py`

- [ ] **Step 1: Write failing tests for GET /api/restocking/recommendations**

Create `tests/backend/test_restocking.py`:

```python
"""Tests for restocking endpoints."""
import pytest
from math import ceil


class TestRestockingRecommendations:
    """Test suite for GET /api/restocking/recommendations."""

    def test_get_recommendations_returns_200(self, client):
        response = client.get("/api/restocking/recommendations")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_recommendation_structure(self, client):
        response = client.get("/api/restocking/recommendations")
        data = response.json()
        assert len(data) > 0
        rec = data[0]
        for field in ["sku", "name", "quantity", "unit_cost", "line_total", "source"]:
            assert field in rec, f"Missing field: {field}"

    def test_recommendation_sources_valid(self, client):
        response = client.get("/api/restocking/recommendations")
        data = response.json()
        valid_sources = {"demand", "low_stock", "both"}
        for rec in data:
            assert rec["source"] in valid_sources, f"Invalid source: {rec['source']}"

    def test_recommendations_sorted_both_first(self, client):
        response = client.get("/api/restocking/recommendations")
        data = response.json()
        source_order = {"both": 0, "low_stock": 1, "demand": 2}
        for i in range(len(data) - 1):
            assert source_order[data[i]["source"]] <= source_order[data[i + 1]["source"]]

    def test_demand_gap_items_included(self, client):
        """Items where forecasted_demand > current_demand should appear."""
        response = client.get("/api/restocking/recommendations")
        data = response.json()
        skus = [r["sku"] for r in data]
        # WDG-001 has demand 300 -> 450 (increasing)
        assert "WDG-001" in skus

    def test_low_stock_items_included(self, client):
        """Items where quantity_on_hand <= reorder_point should appear."""
        response = client.get("/api/restocking/recommendations")
        data = response.json()
        skus = [r["sku"] for r in data]
        # TMP-201: 125 on hand, reorder 150
        assert "TMP-201" in skus

    def test_line_total_calculation(self, client):
        response = client.get("/api/restocking/recommendations")
        data = response.json()
        for rec in data:
            expected = round(rec["quantity"] * rec["unit_cost"], 2)
            assert rec["line_total"] == expected, \
                f"{rec['sku']}: {rec['line_total']} != {expected}"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/vahagn.madatyan/Documents/AnthropicBasecamp/day1/inventory-management && PYTHONPATH=server uv run --directory server python -m pytest tests/backend/test_restocking.py -v`
Expected: FAIL (endpoint doesn't exist yet)

- [ ] **Step 3: Implement GET /api/restocking/recommendations**

Add in `server/main.py` before the `@app.get("/api/reports/quarterly")` line:

```python
@app.get("/api/restocking/recommendations")
def get_restocking_recommendations():
    """Merge demand forecast gaps with low-stock inventory items."""
    from math import ceil
    recommendations = {}

    # Source 1: Demand forecast items where forecasted > current
    for forecast in demand_forecasts:
        if forecast["forecasted_demand"] > forecast["current_demand"]:
            sku = forecast["item_sku"]
            gap = forecast["forecasted_demand"] - forecast["current_demand"]
            unit_cost = forecast.get("unit_cost", 0)
            recommendations[sku] = {
                "sku": sku,
                "name": forecast["item_name"],
                "quantity": gap,
                "unit_cost": unit_cost,
                "line_total": round(gap * unit_cost, 2),
                "source": "demand"
            }

    # Source 2: Inventory items where quantity_on_hand <= reorder_point
    for item in inventory_items:
        if item["quantity_on_hand"] <= item["reorder_point"]:
            sku = item["sku"]
            deficit = item["reorder_point"] - item["quantity_on_hand"]
            qty = deficit + ceil(item["reorder_point"] * 0.2)
            unit_cost = item["unit_cost"]

            if sku in recommendations:
                # Deduplicate: keep higher quantity, mark as "both"
                existing = recommendations[sku]
                recommendations[sku] = {
                    "sku": sku,
                    "name": item["name"],
                    "quantity": max(existing["quantity"], qty),
                    "unit_cost": unit_cost,
                    "line_total": round(max(existing["quantity"], qty) * unit_cost, 2),
                    "source": "both"
                }
            else:
                recommendations[sku] = {
                    "sku": sku,
                    "name": item["name"],
                    "quantity": qty,
                    "unit_cost": unit_cost,
                    "line_total": round(qty * unit_cost, 2),
                    "source": "low_stock"
                }

    # Sort: "both" first, then "low_stock" (by deficit desc), then "demand" (by gap desc)
    source_order = {"both": 0, "low_stock": 1, "demand": 2}
    result = sorted(
        recommendations.values(),
        key=lambda r: (source_order[r["source"]], -r["quantity"])
    )
    return result
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/vahagn.madatyan/Documents/AnthropicBasecamp/day1/inventory-management && PYTHONPATH=server uv run --directory server python -m pytest tests/backend/test_restocking.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add server/main.py tests/backend/test_restocking.py
git commit -m "feat: add restocking recommendations endpoint with tests"
```

---

### Task 4: Backend POST and GET restocking orders endpoints

**Files:**

- Modify: `server/main.py`
- Modify: `tests/backend/test_restocking.py`

- [ ] **Step 1: Write failing tests for POST and GET**

Append to `tests/backend/test_restocking.py`:

```python
class TestRestockingOrders:
    """Test suite for restocking order endpoints."""

    def test_get_restocking_orders_returns_200(self, client):
        response = client.get("/api/restocking-orders")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_submit_restocking_order(self, client):
        order_data = {
            "items": [
                {"sku": "WDG-001", "name": "Industrial Widget Type A",
                 "quantity": 100, "unit_cost": 15.50, "line_total": 1550.00,
                 "source": "demand"}
            ],
            "total_cost": 1550.00,
            "budget": 10000.00
        }
        response = client.post("/api/restocking-orders", json=order_data)
        assert response.status_code == 200
        data = response.json()
        assert data["id"].startswith("RST-")
        assert data["status"] == "Submitted"
        assert "expected_delivery" in data
        assert data["total_cost"] == 1550.00

    def test_submitted_order_appears_in_list(self, client):
        order_data = {
            "items": [
                {"sku": "FLT-405", "name": "Oil Filter Cartridge",
                 "quantity": 50, "unit_cost": 4.50, "line_total": 225.00,
                 "source": "low_stock"}
            ],
            "total_cost": 225.00,
            "budget": 5000.00
        }
        client.post("/api/restocking-orders", json=order_data)
        response = client.get("/api/restocking-orders")
        data = response.json()
        assert len(data) > 0

    def test_expected_delivery_high_cost(self, client):
        """Items >= $200 unit cost should get 14 day delivery."""
        order_data = {
            "items": [
                {"sku": "MTR-304", "name": "Electric Motor 5HP",
                 "quantity": 5, "unit_cost": 285.00, "line_total": 1425.00,
                 "source": "low_stock"}
            ],
            "total_cost": 1425.00,
            "budget": 5000.00
        }
        response = client.post("/api/restocking-orders", json=order_data)
        data = response.json()
        # 14 days from order_date
        from datetime import datetime, timedelta
        order_dt = datetime.fromisoformat(data["order_date"])
        delivery_dt = datetime.fromisoformat(data["expected_delivery"])
        assert (delivery_dt - order_dt).days == 14
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/vahagn.madatyan/Documents/AnthropicBasecamp/day1/inventory-management && PYTHONPATH=server uv run --directory server python -m pytest tests/backend/test_restocking.py::TestRestockingOrders -v`
Expected: FAIL

- [ ] **Step 3: Implement POST and GET endpoints**

Add in `server/main.py` after the recommendations endpoint:

```python
@app.get("/api/restocking-orders")
def get_restocking_orders():
    """Get all submitted restocking orders."""
    return restocking_orders

@app.post("/api/restocking-orders")
def create_restocking_order(request: CreateRestockingOrderRequest):
    """Submit a new restocking order."""
    from datetime import datetime, timedelta

    # Auto-generate ID
    order_num = len(restocking_orders) + 1
    order_id = f"RST-{now.year}-{order_num:04d}"

    # Calculate expected delivery based on max item cost
    max_cost = max((item.unit_cost for item in request.items), default=0)
    if max_cost >= 200:
        lead_days = 14
    elif max_cost >= 50:
        lead_days = 10
    else:
        lead_days = 7

    now = datetime.now()
    expected_delivery = now + timedelta(days=lead_days)

    order = {
        "id": order_id,
        "order_date": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "items": [item.model_dump() for item in request.items],
        "total_cost": request.total_cost,
        "budget": request.budget,
        "status": "Submitted",
        "expected_delivery": expected_delivery.strftime("%Y-%m-%dT%H:%M:%S")
    }

    restocking_orders.append(order)
    return order
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/vahagn.madatyan/Documents/AnthropicBasecamp/day1/inventory-management && PYTHONPATH=server uv run --directory server python -m pytest tests/backend/test_restocking.py -v`
Expected: All PASS

- [ ] **Step 5: Run full test suite for regressions**

Run: `cd /Users/vahagn.madatyan/Documents/AnthropicBasecamp/day1/inventory-management && PYTHONPATH=server uv run --directory server python -m pytest tests/backend/ -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add server/main.py tests/backend/test_restocking.py
git commit -m "feat: add POST/GET restocking orders endpoints with tests"
```

---

### Task 5: Frontend API methods and cleanup

**Files:**

- Modify: `client/src/api.js`
- Modify: `server/main.py` (cleanup)

- [ ] **Step 1: Remove the old `/api/restock/recommendations` endpoint**

The project previously had a `GET /api/restock/recommendations` endpoint (note: `/restock/` not `/restocking/`) with a different response shape. Remove it from `server/main.py` since `GET /api/restocking/recommendations` from Task 3 replaces it. Also remove the old `getRestockRecommendations()` method from `api.js`.

- [ ] **Step 2: Add 3 new API methods**

Add before the closing `}` of the api object:

```javascript
  async getRestockingRecommendations() {
    const response = await axios.get(`${API_BASE_URL}/restocking/recommendations`)
    return response.data
  },

  async getRestockingOrders() {
    const response = await axios.get(`${API_BASE_URL}/restocking-orders`)
    return response.data
  },

  async submitRestockingOrder(data) {
    const response = await axios.post(`${API_BASE_URL}/restocking-orders`, data)
    return response.data
  }
```

- [ ] **Step 3: Commit**

```bash
git add client/src/api.js server/main.py
git commit -m "feat: add restocking API client methods, remove old restock endpoint"
```

---

### Task 6: i18n translations

**Files:**

- Modify: `client/src/locales/en.js`
- Modify: `client/src/locales/ja.js`

- [ ] **Step 1: Add English translations**

Add `restocking: 'Restocking'` to the `nav` section of `en.js`.

Add a new `restocking` section:

```javascript
  restocking: {
    title: 'Restocking',
    description: 'Review recommendations and place restocking orders',
    budget: 'Budget',
    budgetControl: 'Budget Control',
    setBudget: 'Set your restocking budget',
    recommendedItems: 'Recommended Items',
    selectedItems: 'Selected Items',
    estimatedCost: 'Estimated Cost',
    budgetRemaining: 'Budget Remaining',
    overBudget: 'Over Budget',
    placeOrder: 'Place Order',
    submitting: 'Submitting...',
    selectAll: 'Select All',
    deselectAll: 'Deselect All',
    table: {
      select: 'Select',
      name: 'Item Name',
      sku: 'SKU',
      source: 'Source',
      quantity: 'Quantity',
      unitCost: 'Unit Cost',
      lineTotal: 'Line Total'
    },
    sources: {
      demand: 'Demand',
      low_stock: 'Low Stock',
      both: 'Both'
    },
    orderSuccess: 'Order Submitted Successfully',
    orderNumber: 'Order Number',
    expectedDelivery: 'Expected Delivery',
    orderTotal: 'Order Total',
    placeAnother: 'Place Another Order',
    noRecommendations: 'No restocking recommendations at this time'
  },
```

- [ ] **Step 2: Add Japanese translations**

Add `restocking: '補充'` to the `nav` section of `ja.js`.

Add a new `restocking` section:

```javascript
  restocking: {
    title: '補充',
    description: '推奨事項を確認し、補充注文を行う',
    budget: '予算',
    budgetControl: '予算管理',
    setBudget: '補充予算を設定',
    recommendedItems: '推奨品目',
    selectedItems: '選択品目',
    estimatedCost: '見積コスト',
    budgetRemaining: '残り予算',
    overBudget: '予算超過',
    placeOrder: '注文する',
    submitting: '送信中...',
    selectAll: 'すべて選択',
    deselectAll: 'すべて解除',
    table: {
      select: '選択',
      name: '品目名',
      sku: 'SKU',
      source: 'ソース',
      quantity: '数量',
      unitCost: '単価',
      lineTotal: '合計'
    },
    sources: {
      demand: '需要',
      low_stock: '在庫僅少',
      both: '両方'
    },
    orderSuccess: '注文が正常に送信されました',
    orderNumber: '注文番号',
    expectedDelivery: '予定配達日',
    orderTotal: '注文合計',
    placeAnother: '別の注文をする',
    noRecommendations: '現在、補充の推奨事項はありません'
  },
```

- [ ] **Step 3: Commit**

```bash
git add client/src/locales/en.js client/src/locales/ja.js
git commit -m "feat: add restocking i18n translations (EN + JA)"
```

---

### Task 7: Router and navigation

**Files:**

- Modify: `client/src/main.js`
- Modify: `client/src/App.vue`

- [ ] **Step 1: Add route in main.js**

Add import:

```javascript
import Restocking from "./views/Restocking.vue";
```

Add route between demand and spending:

```javascript
{ path: '/restocking', component: Restocking }
```

- [ ] **Step 2: Add nav link in App.vue**

Add between the Demand Forecast and Reports `<router-link>` elements:

```html
<router-link
  to="/restocking"
  :class="{ active: $route.path === '/restocking' }"
>
  {{ t('nav.restocking') }}
</router-link>
```

- [ ] **Step 3: Commit**

```bash
git add client/src/main.js client/src/App.vue
git commit -m "feat: add restocking route and navigation link"
```

---

### Task 8: Create Restocking.vue

**IMPORTANT: Delegate to vue-expert agent per CLAUDE.md mandatory rule.**

**Files:**

- Create: `client/src/views/Restocking.vue`

- [ ] **Step 1: Create Restocking.vue**

The component should have this layout (top to bottom):

1. **Page header**: title + description using i18n
2. **Budget control card**: range slider ($0-$50,000, step $500, default $10,000) + numeric input synced together
3. **Stats grid**: 4 cards — Recommended Items count, Selected Items count, Estimated Cost, Budget Remaining
4. **Recommendations table**: checkbox, item name, SKU, source badge (demand=blue, low_stock=red, both=purple), editable quantity input, unit cost, line total
5. **Budget progress bar**: green (<80%), yellow (80-100%), red (>100%)
6. **Footer**: running total vs budget, "Place Order" button (disabled if over budget or nothing selected)
7. **Success message**: after submission, show order number + expected delivery date + "Place Another Order" button

**Reactive state:**

- `budget` ref (default 10000)
- `recommendations` ref (fetched on mount)
- `selectedItems` reactive map `{ sku: { selected: true, quantity: N } }`
- `loading`, `error`, `submitting`, `submitted`, `submittedOrder` refs

**Computed properties:**

- `selectedList`: filtered items where selected === true
- `runningTotal`: sum of selected items' line totals
- `budgetRemaining`: budget - runningTotal
- `isOverBudget`: runningTotal > budget
- `canSubmit`: selectedList.length > 0 && !isOverBudget && !submitting

**On load:** fetch recommendations, auto-select all items with their default quantities.

**Submit handler:** POST to `/api/restocking-orders` with `{ items: selectedList, total_cost: runningTotal, budget }`. On success, set `submitted = true` and `submittedOrder = response`.

**Style:** Match existing app design system — use `.card`, `.stats-grid`, `.stat-card`, `.badge` classes. Scoped styles for restocking-specific elements (slider, progress bar, success message).

**Currency:** Use `formatCurrency` from `../utils/currency.js` and `currentCurrency` from `useI18n()`.

- [ ] **Step 2: Verify the component renders**

Start servers and navigate to http://localhost:3000/restocking. Verify:

- Page loads without errors
- Budget slider works
- Recommendations table shows items
- Checkboxes toggle selection
- Running total updates

- [ ] **Step 3: Commit**

```bash
git add client/src/views/Restocking.vue
git commit -m "feat: add Restocking tab with budget controls and order submission"
```

---

### Task 9: Add restocking orders section to Orders.vue

**IMPORTANT: Delegate to vue-expert agent per CLAUDE.md mandatory rule.**

**Files:**

- Modify: `client/src/views/Orders.vue`

- [ ] **Step 1: Add restocking orders section**

Below the existing orders table, add a conditional section:

- `v-if="restockingOrders.length > 0"`
- Separate card with title "Submitted Restocking Orders"
- Table columns: Order ID, Date, Items (expandable `<details>`), Total Cost, Status badge (green "Submitted"), Expected Delivery
- Fetch from `api.getRestockingOrders()` on mount alongside existing orders

**Script changes:**

- Import `api.getRestockingOrders`
- Add `restockingOrders` ref
- Fetch in `loadOrders` alongside existing orders fetch
- Add to watch and return

- [ ] **Step 2: Verify integration**

1. Submit an order from the Restocking tab
2. Navigate to Orders tab
3. Verify the "Submitted Restocking Orders" section appears with the order

- [ ] **Step 3: Commit**

```bash
git add client/src/views/Orders.vue
git commit -m "feat: show submitted restocking orders in Orders tab"
```

---

### Task 10: End-to-end verification

- [ ] **Step 1: Run full backend test suite**

Run: `cd /Users/vahagn.madatyan/Documents/AnthropicBasecamp/day1/inventory-management && PYTHONPATH=server uv run --directory server python -m pytest tests/backend/ -v`
Expected: All tests pass

- [ ] **Step 2: Manual E2E test**

1. Start backend: `cd server && uv run python main.py`
2. Start frontend: `cd client && npm run dev`
3. Navigate to Restocking tab — verify items load with budget slider
4. Adjust budget, toggle items, change quantities — verify totals update
5. Submit an order — verify success message
6. Navigate to Orders — verify restocking order appears
7. Switch to Japanese — verify all strings translate

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: complete restocking tab implementation"
```
