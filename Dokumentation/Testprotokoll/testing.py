import os
import sqlite3
import database
import logic
from datetime import datetime, timedelta

def run_backend_tests():
    print("==================================================")
    print("      SMART PANTRY - BACKEND TEST SUITE          ")
    print("==================================================")
    print(f"Test Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("--------------------------------------------------\n")

    # Setup: Reset the database for a clean test environment
    if os.path.exists("smart_pantry_v2.db"):
        os.remove("smart_pantry_v2.db")
    database.init_db()

    # --- TEST 1: Traffic Light Logic ---
    print("[TEST 1] Testing Traffic Light (Color Coding) Logic")
    today = datetime.now()
    
    # Red: Already expired
    expired_date = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    status_red = logic.get_traffic_light_status(expired_date)
    print(f"  - Input: {expired_date} (Expired) -> Result: [{status_red}]")
    assert status_red == "Red"

    # Yellow: Expiring in 2 days
    expiring_soon_date = (today + timedelta(days=2)).strftime('%Y-%m-%d')
    status_yellow = logic.get_traffic_light_status(expiring_soon_date)
    print(f"  - Input: {expiring_soon_date} (Expiring soon) -> Result: [{status_yellow}]")
    assert status_yellow == "Yellow"

    # Green: Expiring in 10 days
    fresh_date = (today + timedelta(days=10)).strftime('%Y-%m-%d')
    status_green = logic.get_traffic_light_status(fresh_date)
    print(f"  - Input: {fresh_date} (Fresh) -> Result: [{status_green}]")
    assert status_green == "Green"
    print("  -> TEST 1 PASSED\n")


    # --- TEST 2: Smart Product Insertion (Merging) ---
    print("[TEST 2] Testing Smart Product Insertion (Merge Logic)")
    
    # Initial insertion
    msg1 = logic.add_smart_product("Milk", 2, "2026-12-31", "Dairy")
    print(f"  - Step 1: Add 'Milk' (2x) -> {msg1}")
    
    # Duplicate insertion (same name & date) -> Should merge quantities
    msg2 = logic.add_smart_product("Milk", 3, "2026-12-31", "Dairy")
    print(f"  - Step 2: Add 'Milk' (3x) again -> {msg2}")
    
    products = database.get_all_products()
    milk = next(p for p in products if p['name'] == "Milk")
    print(f"  - Current state: {milk['name']} quantity is {milk['quantity']}")
    assert milk['quantity'] == 5 # 2 + 3
    
    # Different date -> Should be a separate entry
    msg3 = logic.add_smart_product("Milk", 1, "2027-01-10", "Dairy")
    print(f"  - Step 3: Add 'Milk' (1x) with different date -> {msg3}")
    
    products = database.get_all_products()
    milk_entries = [p for p in products if p['name'] == "Milk"]
    print(f"  - Number of 'Milk' entries: {len(milk_entries)}")
    assert len(milk_entries) == 2
    print("  -> TEST 2 PASSED\n")


    # --- TEST 3: Filtering & Search ---
    print("[TEST 3] Testing Filtering and Search Logic")
    logic.add_smart_product("Apple", 5, "2026-06-01", "Fruit")
    logic.add_smart_product("Orange", 3, "2026-06-01", "Fruit")
    logic.add_smart_product("Chocolate", 1, "2026-12-31", "Snack")
    
    # Search for "app"
    filtered_app = logic.filter_products(query="app")
    print(f"  - Search for 'app': Found {len(filtered_app)} item(s) ([{filtered_app[0]['name'] if filtered_app else 'None'}])")
    assert len(filtered_app) == 1
    assert filtered_app[0]['name'] == "Apple"
    
    # Filter by Category "Fruit"
    filtered_fruit = logic.filter_products(category="Fruit")
    fruit_names = [p['name'] for p in filtered_fruit]
    print(f"  - Category filter 'Fruit': Found {len(filtered_fruit)} item(s) {fruit_names}")
    assert len(filtered_fruit) == 2
    assert "Apple" in fruit_names and "Orange" in fruit_names
    
    # Unique Categories
    cats = logic.get_unique_categories()
    print(f"  - Unique Categories Found: {cats}")
    assert "Dairy" in cats
    assert "Fruit" in cats
    assert "Snack" in cats
    assert "All" in cats
    print("  -> TEST 3 PASSED\n")


    # --- TEST 4: Statistics Tracking ---
    print("[TEST 4] Testing Stats (Consumed vs. Wasted)")
    
    # Get initial milk ID
    milk_id = milk['id']
    
    # Consume 2 Milk
    database.update_quantity(milk_id, 3, status="consumed", change_amount=-2)
    print(f"  - Action: Consumed 2 units of Milk.")
    
    # Waste 1 Milk
    database.update_quantity(milk_id, 2, status="wasted", change_amount=-1)
    print(f"  - Action: Wasted 1 unit of Milk.")
    
    stats_str = logic.get_formatted_stats()
    print(f"  - Generated Statistics:\n{stats_str}")
    
    stats = database.get_stats()
    assert stats['consumed'] == 2
    assert stats['wasted'] == 1
    print("  -> TEST 4 PASSED\n")

    print("==================================================")
    print("         ALL BACKEND TESTS COMPLETED              ")
    print("==================================================")

if __name__ == "__main__":
    run_backend_tests()
