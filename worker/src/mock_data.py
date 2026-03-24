"""
KV-based data loader for Cloudflare Python Worker.
Loads JSON data from KV namespace instead of filesystem.
"""

import json


async def _get_json(kv, key: str, default=None):
    """Get and parse a JSON value from KV. Raises on missing required keys."""
    raw = await kv.get(key)
    if raw is None:
        if default is not None:
            return default
        raise RuntimeError(f"Required KV key '{key}' is missing. Run seed-kv.sh.")
    return json.loads(raw)


async def load_data_from_kv(kv):
    """Load all datasets from Cloudflare KV namespace."""
    inventory_items = await _get_json(kv, "data:inventory")
    orders = await _get_json(kv, "data:orders")
    demand_forecasts = await _get_json(kv, "data:demand_forecasts")
    backlog_items = await _get_json(kv, "data:backlog_items")
    spending_data = await _get_json(kv, "data:spending")
    recent_transactions = await _get_json(kv, "data:transactions")
    purchase_orders = await _get_json(kv, "data:purchase_orders")
    restocking_orders = await _get_json(kv, "data:restocking_orders", default=[])

    return {
        "inventory_items": inventory_items,
        "orders": orders,
        "demand_forecasts": demand_forecasts,
        "backlog_items": backlog_items,
        "spending_summary": spending_data["spending_summary"],
        "monthly_spending": spending_data["monthly_spending"],
        "category_spending": spending_data["category_spending"],
        "recent_transactions": recent_transactions,
        "purchase_orders": purchase_orders,
        "restocking_orders": restocking_orders,
    }
