"""
FastAPI app for Cloudflare Python Worker.
Adapted from server/main.py — same endpoints, same logic, data from KV.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel

from mock_data import load_data_from_kv

app = FastAPI(title="Factory Inventory Management System")


@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    """Manual CORS handling to avoid serialization issues with CORSMiddleware."""
    if request.method == "OPTIONS":
        return JSONResponse(
            content="",
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Max-Age": "86400",
            },
        )
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Quarter mapping for date filtering
QUARTER_MAP = {
    "Q1-2025": ["2025-01", "2025-02", "2025-03"],
    "Q2-2025": ["2025-04", "2025-05", "2025-06"],
    "Q3-2025": ["2025-07", "2025-08", "2025-09"],
    "Q4-2025": ["2025-10", "2025-11", "2025-12"],
}


def filter_by_month(items: list, month: Optional[str]) -> list:
    """Filter items by month/quarter based on order_date field"""
    if not month or month == "all":
        return items
    if month.startswith("Q"):
        if month in QUARTER_MAP:
            months = QUARTER_MAP[month]
            return [
                item
                for item in items
                if any(m in item.get("order_date", "") for m in months)
            ]
    else:
        return [item for item in items if month in item.get("order_date", "")]
    return items


def apply_filters(
    items: list,
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
) -> list:
    """Apply common filters to a list of items"""
    filtered = items
    if warehouse and warehouse != "all":
        filtered = [item for item in filtered if item.get("warehouse") == warehouse]
    if category and category != "all":
        filtered = [
            item
            for item in filtered
            if item.get("category", "").lower() == category.lower()
        ]
    if status and status != "all":
        filtered = [
            item
            for item in filtered
            if item.get("status", "").lower() == status.lower()
        ]
    return filtered


# --- Pydantic Models ---


class InventoryItem(BaseModel):
    id: str
    sku: str
    name: str
    category: str
    warehouse: str
    quantity_on_hand: int
    reorder_point: int
    unit_cost: float
    location: str
    last_updated: str


class Order(BaseModel):
    id: str
    order_number: str
    customer: str
    items: List[dict]
    status: str
    order_date: str
    expected_delivery: str
    total_value: float
    actual_delivery: Optional[str] = None
    warehouse: Optional[str] = None
    category: Optional[str] = None


class DemandForecast(BaseModel):
    id: str
    item_sku: str
    item_name: str
    current_demand: int
    forecasted_demand: int
    trend: str
    period: str
    lead_time_days: Optional[int] = None
    supplier: Optional[str] = None
    unit_cost: Optional[float] = None


class BacklogItem(BaseModel):
    id: str
    order_id: str
    item_sku: str
    item_name: str
    quantity_needed: int
    quantity_available: int
    days_delayed: int
    priority: str
    has_purchase_order: Optional[bool] = False


class PurchaseOrder(BaseModel):
    id: str
    backlog_item_id: Optional[str] = None
    item_sku: Optional[str] = None
    item_name: Optional[str] = None
    supplier_name: str
    quantity: int
    unit_cost: float
    expected_delivery_date: str
    status: str
    created_date: str
    notes: Optional[str] = None


class CreatePurchaseOrderRequest(BaseModel):
    backlog_item_id: str
    supplier_name: str
    quantity: int
    unit_cost: float
    expected_delivery_date: str
    notes: Optional[str] = None


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


# --- Helper: get data from KV via request scope ---


async def get_data(request: Request) -> dict:
    """Load data from KV. The env is passed through by asgi.fetch()."""
    env = request.scope["env"]
    return await load_data_from_kv(env.INVENTORY_KV)


# --- API Endpoints ---


@app.get("/")
async def root():
    return {"message": "Factory Inventory Management System API", "version": "1.0.0"}


@app.get("/api/inventory", response_model=List[InventoryItem])
async def get_inventory(
    request: Request,
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
):
    data = await get_data(request)
    return apply_filters(data["inventory_items"], warehouse, category)


@app.get("/api/inventory/{item_id}", response_model=InventoryItem)
async def get_inventory_item(request: Request, item_id: str):
    data = await get_data(request)
    item = next(
        (item for item in data["inventory_items"] if item["id"] == item_id), None
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.get("/api/orders", response_model=List[Order])
async def get_orders(
    request: Request,
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None,
):
    data = await get_data(request)
    filtered_orders = apply_filters(data["orders"], warehouse, category, status)
    filtered_orders = filter_by_month(filtered_orders, month)
    return filtered_orders


@app.get("/api/orders/{order_id}", response_model=Order)
async def get_order(request: Request, order_id: str):
    data = await get_data(request)
    order = next((o for o in data["orders"] if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.get("/api/demand", response_model=List[DemandForecast])
async def get_demand_forecasts(request: Request):
    data = await get_data(request)
    return data["demand_forecasts"]


@app.get("/api/backlog", response_model=List[BacklogItem])
async def get_backlog(request: Request):
    data = await get_data(request)
    result = []
    for item in data["backlog_items"]:
        item_dict = dict(item)
        has_po = any(
            po["backlog_item_id"] == item["id"] for po in data["purchase_orders"]
        )
        item_dict["has_purchase_order"] = has_po
        result.append(item_dict)
    return result


@app.get("/api/dashboard/summary")
async def get_dashboard_summary(
    request: Request,
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None,
):
    data = await get_data(request)
    filtered_inventory = apply_filters(data["inventory_items"], warehouse, category)
    filtered_orders = apply_filters(data["orders"], warehouse, category, status)
    filtered_orders = filter_by_month(filtered_orders, month)

    total_inventory_value = sum(
        item["quantity_on_hand"] * item["unit_cost"] for item in filtered_inventory
    )
    low_stock_items = len(
        [
            item
            for item in filtered_inventory
            if item["quantity_on_hand"] <= item["reorder_point"]
        ]
    )
    pending_orders = len(
        [
            order
            for order in filtered_orders
            if order["status"] in ["Processing", "Backordered"]
        ]
    )
    total_backlog_items = len(data["backlog_items"])

    return {
        "total_inventory_value": round(total_inventory_value, 2),
        "low_stock_items": low_stock_items,
        "pending_orders": pending_orders,
        "total_backlog_items": total_backlog_items,
        "total_orders_value": sum(
            order["total_value"] for order in filtered_orders
        ),
    }


@app.get("/api/spending/summary")
async def get_spending_summary(request: Request):
    data = await get_data(request)
    return data["spending_summary"]


@app.get("/api/spending/monthly")
async def get_monthly_spending(request: Request):
    data = await get_data(request)
    return data["monthly_spending"]


@app.get("/api/spending/categories")
async def get_category_spending(request: Request):
    data = await get_data(request)
    return data["category_spending"]


@app.get("/api/spending/transactions")
async def get_recent_transactions(request: Request):
    data = await get_data(request)
    return data["recent_transactions"]


@app.get("/api/purchase-orders")
async def get_purchase_orders(request: Request):
    data = await get_data(request)
    return data["purchase_orders"]


@app.get("/api/restocking/recommendations")
async def get_restocking_recommendations(request: Request):
    from math import ceil

    data = await get_data(request)
    recommendations = {}

    for forecast in data["demand_forecasts"]:
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
                "source": "demand",
            }

    for item in data["inventory_items"]:
        if item["quantity_on_hand"] <= item["reorder_point"]:
            sku = item["sku"]
            deficit = item["reorder_point"] - item["quantity_on_hand"]
            qty = deficit + ceil(item["reorder_point"] * 0.2)
            unit_cost = item["unit_cost"]

            if sku in recommendations:
                existing = recommendations[sku]
                recommendations[sku] = {
                    "sku": sku,
                    "name": item["name"],
                    "quantity": max(existing["quantity"], qty),
                    "unit_cost": unit_cost,
                    "line_total": round(
                        max(existing["quantity"], qty) * unit_cost, 2
                    ),
                    "source": "both",
                }
            else:
                recommendations[sku] = {
                    "sku": sku,
                    "name": item["name"],
                    "quantity": qty,
                    "unit_cost": unit_cost,
                    "line_total": round(qty * unit_cost, 2),
                    "source": "low_stock",
                }

    source_order = {"both": 0, "low_stock": 1, "demand": 2}
    result = sorted(
        recommendations.values(),
        key=lambda r: (source_order[r["source"]], -r["quantity"]),
    )
    return result


@app.get("/api/restocking-orders")
async def get_restocking_orders(request: Request):
    data = await get_data(request)
    return data["restocking_orders"]


@app.post("/api/restocking-orders")
async def create_restocking_order(
    request: Request, body: CreateRestockingOrderRequest
):
    import json
    from datetime import datetime, timedelta

    data = await get_data(request)
    env = request.scope["env"]
    now = datetime.now()

    order_num = len(data["restocking_orders"]) + 1
    order_id = f"RST-{now.year}-{order_num:04d}"

    max_cost = max((item.unit_cost for item in body.items), default=0)
    if max_cost >= 200:
        lead_days = 14
    elif max_cost >= 50:
        lead_days = 10
    else:
        lead_days = 7

    expected_delivery = now + timedelta(days=lead_days)

    order = {
        "id": order_id,
        "order_date": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "items": [item.model_dump() for item in body.items],
        "total_cost": body.total_cost,
        "budget": body.budget,
        "status": "Submitted",
        "expected_delivery": expected_delivery.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    # Persist to KV without mutating the loaded data
    updated_orders = data["restocking_orders"] + [order]
    await env.INVENTORY_KV.put(
        "data:restocking_orders", json.dumps(updated_orders)
    )
    return order


@app.get("/api/reports/quarterly")
async def get_quarterly_reports(
    request: Request,
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None,
):
    data = await get_data(request)
    filtered_orders = data["orders"]

    if warehouse and warehouse != "all":
        filtered_orders = [
            o
            for o in filtered_orders
            if any(
                item.get("warehouse") == warehouse for item in o.get("items", [])
            )
        ]
    if category and category != "all":
        filtered_orders = [
            o
            for o in filtered_orders
            if any(
                item.get("category", "").lower() == category.lower()
                for item in o.get("items", [])
            )
        ]
    if status and status != "all":
        filtered_orders = [
            o for o in filtered_orders if o.get("status") == status
        ]
    if month and month != "all":
        filtered_orders = [
            o
            for o in filtered_orders
            if o.get("order_date", "").startswith(month)
        ]

    quarters = {}
    for order in filtered_orders:
        order_date = order.get("order_date", "")
        if "2025-01" in order_date or "2025-02" in order_date or "2025-03" in order_date:
            quarter = "Q1-2025"
        elif "2025-04" in order_date or "2025-05" in order_date or "2025-06" in order_date:
            quarter = "Q2-2025"
        elif "2025-07" in order_date or "2025-08" in order_date or "2025-09" in order_date:
            quarter = "Q3-2025"
        elif "2025-10" in order_date or "2025-11" in order_date or "2025-12" in order_date:
            quarter = "Q4-2025"
        else:
            continue

        if quarter not in quarters:
            quarters[quarter] = {
                "quarter": quarter,
                "total_orders": 0,
                "total_revenue": 0,
                "delivered_orders": 0,
                "avg_order_value": 0,
            }

        quarters[quarter]["total_orders"] += 1
        quarters[quarter]["total_revenue"] += order.get("total_value", 0)
        if order.get("status") == "Delivered":
            quarters[quarter]["delivered_orders"] += 1

    result = []
    for q, qdata in quarters.items():
        if qdata["total_orders"] > 0:
            qdata["avg_order_value"] = round(
                qdata["total_revenue"] / qdata["total_orders"], 2
            )
            qdata["fulfillment_rate"] = round(
                (qdata["delivered_orders"] / qdata["total_orders"]) * 100, 1
            )
        result.append(qdata)

    result.sort(key=lambda x: x["quarter"])
    return result


@app.get("/api/reports/monthly-trends")
async def get_monthly_trends(
    request: Request,
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None,
):
    data = await get_data(request)
    filtered_orders = data["orders"]

    if warehouse and warehouse != "all":
        filtered_orders = [
            o
            for o in filtered_orders
            if any(
                item.get("warehouse") == warehouse for item in o.get("items", [])
            )
        ]
    if category and category != "all":
        filtered_orders = [
            o
            for o in filtered_orders
            if any(
                item.get("category", "").lower() == category.lower()
                for item in o.get("items", [])
            )
        ]
    if status and status != "all":
        filtered_orders = [
            o for o in filtered_orders if o.get("status") == status
        ]
    if month and month != "all":
        filtered_orders = [
            o
            for o in filtered_orders
            if o.get("order_date", "").startswith(month)
        ]

    months = {}
    for order in filtered_orders:
        order_date = order.get("order_date", "")
        if not order_date:
            continue
        m = order_date[:7]
        if m not in months:
            months[m] = {
                "month": m,
                "order_count": 0,
                "revenue": 0,
                "delivered_count": 0,
            }
        months[m]["order_count"] += 1
        months[m]["revenue"] += order.get("total_value", 0)
        if order.get("status") == "Delivered":
            months[m]["delivered_count"] += 1

    result = list(months.values())
    result.sort(key=lambda x: x["month"])
    return result
