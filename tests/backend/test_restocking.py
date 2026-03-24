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
        from datetime import datetime
        order_dt = datetime.fromisoformat(data["order_date"])
        delivery_dt = datetime.fromisoformat(data["expected_delivery"])
        assert (delivery_dt - order_dt).days == 14
