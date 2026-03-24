"""
Tests for miscellaneous API endpoints (demand, backlog, spending).
"""
import pytest


class TestDemandEndpoints:
    """Test suite for demand forecast endpoints."""

    def test_get_demand_forecasts(self, client):
        """Test getting demand forecasts."""
        response = client.get("/api/demand")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # Check structure if data exists
        if len(data) > 0:
            forecast = data[0]
            assert "id" in forecast
            assert "item_sku" in forecast
            assert "item_name" in forecast
            assert "current_demand" in forecast
            assert "forecasted_demand" in forecast
            assert "trend" in forecast
            assert "period" in forecast

    def test_demand_forecast_trends(self, client):
        """Test that demand forecasts have valid trend values."""
        response = client.get("/api/demand")
        data = response.json()

        valid_trends = ["increasing", "stable", "decreasing"]

        for forecast in data:
            assert forecast["trend"].lower() in valid_trends

    def test_demand_forecast_values(self, client):
        """Test that demand forecast values are non-negative."""
        response = client.get("/api/demand")
        data = response.json()

        for forecast in data:
            assert forecast["current_demand"] >= 0
            assert forecast["forecasted_demand"] >= 0

    def test_stable_demand_items_have_small_changes(self, client):
        """Test that items with 'stable' trend have less than 2% change."""
        response = client.get("/api/demand")
        data = response.json()

        stable_items = [item for item in data if item["trend"].lower() == "stable"]

        # Should have at least 5 stable items
        assert len(stable_items) >= 5, f"Expected at least 5 stable items, found {len(stable_items)}"

        for item in stable_items:
            current = item["current_demand"]
            forecasted = item["forecasted_demand"]

            # Calculate percentage change
            if current > 0:
                percent_change = abs((forecasted - current) / current) * 100
                assert percent_change < 2.0, \
                    f"Item {item['item_name']} has {percent_change:.2f}% change, expected < 2%"

    def test_demand_forecast_has_new_items(self, client):
        """Test that new demand forecast items exist."""
        response = client.get("/api/demand")
        data = response.json()

        # Check for the new items we added
        skus = [item["item_sku"] for item in data]

        # Should have Temperature Sensor Module and Logic Controller Board
        assert "SNR-420" in skus, "Missing Temperature Sensor Module"
        assert "CTL-330" in skus, "Missing Logic Controller Board"

        # Verify they are marked as stable
        for item in data:
            if item["item_sku"] in ["SNR-420", "CTL-330"]:
                assert item["trend"].lower() == "stable", \
                    f"New item {item['item_name']} should have stable trend"


class TestBacklogEndpoints:
    """Test suite for backlog endpoints."""

    def test_get_backlog(self, client):
        """Test getting backlog items."""
        response = client.get("/api/backlog")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # Check structure if data exists
        if len(data) > 0:
            backlog_item = data[0]
            assert "id" in backlog_item
            assert "order_id" in backlog_item
            assert "item_sku" in backlog_item
            assert "item_name" in backlog_item
            assert "quantity_needed" in backlog_item
            assert "quantity_available" in backlog_item
            assert "days_delayed" in backlog_item
            assert "priority" in backlog_item

    def test_backlog_priority_values(self, client):
        """Test that backlog items have valid priority values."""
        response = client.get("/api/backlog")
        data = response.json()

        valid_priorities = ["high", "medium", "low"]

        for item in data:
            assert item["priority"].lower() in valid_priorities

    def test_backlog_quantity_logic(self, client):
        """Test that backlog quantities are non-negative."""
        response = client.get("/api/backlog")
        data = response.json()

        for item in data:
            # Quantities should be non-negative
            assert item["quantity_needed"] >= 0
            assert item["quantity_available"] >= 0

    def test_backlog_days_delayed(self, client):
        """Test that days delayed is non-negative."""
        response = client.get("/api/backlog")
        data = response.json()

        for item in data:
            assert item["days_delayed"] >= 0


class TestSpendingEndpoints:
    """Test suite for spending-related endpoints."""

    def test_get_spending_summary(self, client):
        """Test getting spending summary."""
        response = client.get("/api/spending/summary")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)

    def test_get_monthly_spending(self, client):
        """Test getting monthly spending data."""
        response = client.get("/api/spending/monthly")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # Check structure if data exists
        if len(data) > 0:
            month_data = data[0]
            assert "month" in month_data or "period" in month_data

    def test_monthly_spending_has_all_cost_categories(self, client):
        """Test that monthly spending includes all cost categories."""
        response = client.get("/api/spending/monthly")
        data = response.json()

        required_fields = ["procurement", "operational", "labor", "overhead"]

        for month_data in data:
            for field in required_fields:
                assert field in month_data, f"Missing {field} in monthly spending"
                assert isinstance(month_data[field], (int, float))
                assert month_data[field] >= 0

    def test_monthly_spending_has_variety(self, client):
        """Test that monthly spending data has variety (not all the same)."""
        response = client.get("/api/spending/monthly")
        data = response.json()

        # Collect all procurement values
        procurement_values = [month["procurement"] for month in data]

        # Should have at least 3 different values (variety)
        unique_values = set(procurement_values)
        assert len(unique_values) >= 3, \
            "Monthly spending should have variety, not all the same values"

        # Same for other categories
        operational_values = set(month["operational"] for month in data)
        assert len(operational_values) >= 3, \
            "Operational costs should have variety across months"

    def test_get_category_spending(self, client):
        """Test getting spending by category."""
        response = client.get("/api/spending/categories")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # Check structure if data exists
        if len(data) > 0:
            category_data = data[0]
            assert "category" in category_data or "name" in category_data

    def test_get_recent_transactions(self, client):
        """Test getting recent transactions."""
        response = client.get("/api/spending/transactions")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # Check structure if data exists
        if len(data) > 0:
            transaction = data[0]
            # Transactions should have some identifying fields
            assert isinstance(transaction, dict)


class TestPurchaseOrderEndpoints:
    """Test suite for purchase order endpoints."""

    def test_get_purchase_orders(self, client):
        """Test getting all purchase orders."""
        response = client.get("/api/purchase-orders")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_purchase_order_structure(self, client):
        """Test that purchase orders have required fields."""
        response = client.get("/api/purchase-orders")
        data = response.json()

        required_fields = ["id", "supplier_name", "quantity", "unit_cost",
                           "expected_delivery_date", "status", "created_date"]

        for po in data:
            for field in required_fields:
                assert field in po, f"Missing {field} in purchase order {po.get('id')}"

    def test_purchase_orders_have_item_info(self, client):
        """Test that purchase orders include item SKU and name."""
        response = client.get("/api/purchase-orders")
        data = response.json()

        for po in data:
            assert "item_sku" in po
            assert "item_name" in po
            assert po["item_sku"] is not None
            assert po["item_name"] is not None

    def test_purchase_orders_cover_backlog_items(self, client):
        """Test that all backlog items have corresponding purchase orders."""
        backlog_response = client.get("/api/backlog")
        backlog_data = backlog_response.json()

        po_response = client.get("/api/purchase-orders")
        po_data = po_response.json()

        backlog_skus = {item["item_sku"] for item in backlog_data}
        po_skus = {po["item_sku"] for po in po_data}

        for sku in backlog_skus:
            assert sku in po_skus, f"Backlog item {sku} has no purchase order"

    def test_purchase_order_valid_statuses(self, client):
        """Test that purchase orders have valid status values."""
        response = client.get("/api/purchase-orders")
        data = response.json()

        valid_statuses = ["Pending", "Confirmed", "Shipped", "Delivered", "Cancelled"]
        for po in data:
            assert po["status"] in valid_statuses, \
                f"Invalid PO status: {po['status']}"


class TestRestockRecommendations:
    """Test suite for restock recommendation endpoints."""

    def test_get_restock_recommendations(self, client):
        """Test getting restock recommendations."""
        response = client.get("/api/restock/recommendations")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_restock_recommendation_structure(self, client):
        """Test that recommendations have required fields."""
        response = client.get("/api/restock/recommendations")
        data = response.json()

        required_fields = ["sku", "name", "category", "warehouse",
                           "quantity_on_hand", "reorder_point",
                           "pending_po_quantity", "suggested_order_quantity",
                           "estimated_cost", "urgency"]

        for rec in data:
            for field in required_fields:
                assert field in rec, f"Missing {field} in recommendation for {rec.get('sku')}"

    def test_restock_urgency_values(self, client):
        """Test that urgency values are valid."""
        response = client.get("/api/restock/recommendations")
        data = response.json()

        valid_urgencies = ["critical", "high", "medium"]
        for rec in data:
            assert rec["urgency"] in valid_urgencies, \
                f"Invalid urgency: {rec['urgency']} for {rec['sku']}"

    def test_restock_sorted_by_urgency(self, client):
        """Test that recommendations are sorted by urgency (critical first)."""
        response = client.get("/api/restock/recommendations")
        data = response.json()

        urgency_order = {"critical": 0, "high": 1, "medium": 2}
        for i in range(len(data) - 1):
            current = urgency_order[data[i]["urgency"]]
            next_item = urgency_order[data[i + 1]["urgency"]]
            assert current <= next_item, \
                f"Recommendations not sorted: {data[i]['urgency']} before {data[i+1]['urgency']}"

    def test_restock_suggested_qty_non_negative(self, client):
        """Test that suggested quantities and costs are non-negative."""
        response = client.get("/api/restock/recommendations")
        data = response.json()

        for rec in data:
            assert rec["suggested_order_quantity"] >= 0, \
                f"Negative suggested qty for {rec['sku']}"
            assert rec["estimated_cost"] >= 0, \
                f"Negative estimated cost for {rec['sku']}"

    def test_restock_includes_below_reorder_items(self, client):
        """Test that items below reorder point appear in recommendations."""
        inv_response = client.get("/api/inventory")
        inv_data = inv_response.json()

        below_reorder_skus = {
            item["sku"] for item in inv_data
            if item["quantity_on_hand"] <= item["reorder_point"]
        }

        rec_response = client.get("/api/restock/recommendations")
        rec_data = rec_response.json()
        rec_skus = {rec["sku"] for rec in rec_data}

        for sku in below_reorder_skus:
            assert sku in rec_skus, \
                f"Below-reorder item {sku} missing from recommendations"

    def test_restock_includes_backlog_shortage(self, client):
        """Test that recommendations include backlog shortage info."""
        response = client.get("/api/restock/recommendations")
        data = response.json()

        for rec in data:
            assert "backlog_shortage" in rec
            assert "effective_available" in rec
            assert rec["backlog_shortage"] >= 0

    def test_backlog_items_are_critical(self, client):
        """Test that items with backlog shortages are marked critical."""
        backlog_response = client.get("/api/backlog")
        backlog_data = backlog_response.json()
        backlog_skus = {item["item_sku"] for item in backlog_data
                        if item["quantity_needed"] > item["quantity_available"]}

        rec_response = client.get("/api/restock/recommendations")
        rec_data = rec_response.json()

        for rec in rec_data:
            if rec["sku"] in backlog_skus:
                assert rec["urgency"] == "critical", \
                    f"Backlog item {rec['sku']} should be critical, got {rec['urgency']}"


class TestRootEndpoint:
    """Test suite for root endpoint."""

    def test_root_endpoint(self, client):
        """Test the root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data or "version" in data

    def test_root_endpoint_structure(self, client):
        """Test root endpoint has expected structure."""
        response = client.get("/")
        data = response.json()

        # Should have message and version
        assert "message" in data
        assert "version" in data
        assert isinstance(data["message"], str)
        assert isinstance(data["version"], str)
