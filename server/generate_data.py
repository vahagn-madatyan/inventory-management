"""
Script to generate sample data spread across all months of 2025

Pricing model:
- inventory.json unit_cost = purchase/procurement cost
- orders.json unit_price = sell price to customer (typically 1.5x-3x of unit_cost)
- The 'price' field below is the SELL price used in orders
"""
import json
import random
from datetime import datetime, timedelta

# Product catalog - prices are SELL prices (customer-facing)
# Purchase costs are defined in inventory.json as unit_cost
products = [
    {"sku": "PCB-001", "name": "Single Layer PCB Assembly", "category": "Circuit Boards", "price": 49.99},
    {"sku": "PCB-002", "name": "Dual Layer PCB Assembly", "category": "Circuit Boards", "price": 59.99},
    {"sku": "PCB-003", "name": "Multi Layer PCB Assembly", "category": "Circuit Boards", "price": 69.00},
    {"sku": "TMP-201", "name": "Temperature Sensor Module", "category": "Sensors", "price": 179.00},
    {"sku": "HMD-202", "name": "Humidity Sensor Module", "category": "Sensors", "price": 249.00},
    {"sku": "PRS-203", "name": "Pressure Sensor Module", "category": "Sensors", "price": 25.50},
    {"sku": "PRX-204", "name": "Proximity Sensor", "category": "Sensors", "price": 16.99},
    {"sku": "ULS-205", "name": "Ultrasonic Distance Sensor", "category": "Sensors", "price": 31.99},
    {"sku": "SRV-301", "name": "Micro Servo Motor", "category": "Actuators", "price": 890.00},
    {"sku": "SRV-302", "name": "Standard Servo Motor", "category": "Actuators", "price": 1450.00},
    {"sku": "STP-303", "name": "Stepper Motor NEMA 17", "category": "Actuators", "price": 649.00},
    {"sku": "MCU-401", "name": "8-bit Microcontroller", "category": "Controllers", "price": 16.50},
    {"sku": "MCU-402", "name": "32-bit ARM Microcontroller", "category": "Controllers", "price": 12.99},
    {"sku": "DSP-403", "name": "Digital Signal Processor", "category": "Controllers", "price": 15.50},
    {"sku": "WDG-001", "name": "Industrial Widget Type A", "category": "Mechanical Parts", "price": 24.99},
    {"sku": "BRG-102", "name": "Steel Bearing Assembly", "category": "Mechanical Parts", "price": 57.50},
    {"sku": "GSK-203", "name": "High-Temperature Gasket", "category": "Mechanical Parts", "price": 12.75},
    {"sku": "MTR-304", "name": "Electric Motor 5HP", "category": "Actuators", "price": 445.00},
    {"sku": "FLT-405", "name": "Oil Filter Cartridge", "category": "Mechanical Parts", "price": 8.25},
    {"sku": "VLV-506", "name": "Pressure Relief Valve", "category": "Mechanical Parts", "price": 84.00},
    {"sku": "PSU-501", "name": "5V 10A Switching Power Supply", "category": "Power Supplies", "price": 37.99},
    {"sku": "PSU-502", "name": "12V 5A Power Supply Module", "category": "Power Supplies", "price": 44.99},
    {"sku": "PSU-506", "name": "USB-C PD 100W Power Supply", "category": "Power Supplies", "price": 59.99},
]

customers = [
    "Acme Manufacturing Corp", "TechBuild Industries", "Global Parts Ltd",
    "Precision Tools Inc", "Industrial Solutions Inc", "MegaCorp Industries",
    "BuildTech Co", "FastAssembly Ltd", "Quality Parts LLC", "Superior Manufacturing",
    "PrecisionWorks Inc", "Elite Systems Corp", "Advanced Components Inc",
    "ProManufacturing LLC", "TechSolutions Group", "Innovative Parts Co",
    "Premier Industries", "Dynamic Systems Ltd", "Quantum Manufacturing",
    "Apex Engineering", "Titan Products Inc", "Vanguard Systems",
    "Omega Manufacturing", "Fusion Industries", "Stellar Components Ltd",
    "Nexus Engineering", "Cascade Manufacturing", "Horizon Technologies",
    "Summit Parts Corp", "Velocity Industries"
]

warehouses = ["San Francisco", "London", "Tokyo"]
statuses = ["Delivered", "Shipped", "Processing", "Backordered"]

# Generate orders for each month of 2025
orders = []
order_id = 1

for month in range(1, 13):  # Jan to Dec
    # Generate 8-12 orders per month
    num_orders = random.randint(8, 12)

    for _ in range(num_orders):
        # Random day in the month
        day = random.randint(1, 28)  # Using 28 to avoid month-end issues
        hour = random.randint(8, 17)
        minute = random.randint(0, 59)

        order_date = f"2025-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00"

        # Expected delivery 7-14 days later
        order_datetime = datetime(2025, month, day, hour, minute)
        delivery_days = random.randint(7, 14)
        expected_delivery = order_datetime + timedelta(days=delivery_days)

        # Determine status based on date (earlier orders more likely to be delivered)
        if month <= 8:
            status = random.choices(statuses, weights=[70, 20, 5, 5])[0]
        elif month <= 10:
            status = random.choices(statuses, weights=[40, 40, 15, 5])[0]
        else:
            status = random.choices(statuses, weights=[10, 30, 40, 20])[0]

        # Select 1-3 products for the order
        num_items = random.randint(1, 3)
        order_products = random.sample(products, num_items)

        items = []
        total_value = 0
        primary_category = None

        for product in order_products:
            quantity = random.randint(50, 1000)
            item_value = quantity * product["price"]
            total_value += item_value

            if primary_category is None:
                primary_category = product["category"]

            items.append({
                "sku": product["sku"],
                "name": product["name"],
                "quantity": quantity,
                "unit_price": product["price"]
            })

        warehouse = random.choice(warehouses)

        order = {
            "id": str(order_id),
            "order_number": f"ORD-2025-{order_id:04d}",
            "customer": random.choice(customers),
            "items": items,
            "status": status,
            "warehouse": warehouse,
            "category": primary_category,
            "order_date": order_date,
            "expected_delivery": expected_delivery.strftime("%Y-%m-%dT%H:%M:%S"),
            "total_value": round(total_value, 2)
        }

        if status == "Delivered" and month <= 10:
            actual_delivery = order_datetime + timedelta(days=random.randint(6, delivery_days + 2))
            order["actual_delivery"] = actual_delivery.strftime("%Y-%m-%dT%H:%M:%S")

        orders.append(order)
        order_id += 1

# Save to file
with open('data/orders.json', 'w') as f:
    json.dump(orders, f, indent=2)

print(f"Generated {len(orders)} orders across 12 months of 2025")

# Count orders per month
from collections import defaultdict
orders_per_month = defaultdict(int)
for order in orders:
    month = order['order_date'][5:7]
    orders_per_month[month] += 1

print("\nOrders per month:")
for month in sorted(orders_per_month.keys()):
    print(f"  {month}: {orders_per_month[month]} orders")
