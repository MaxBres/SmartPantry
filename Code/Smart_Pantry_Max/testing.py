import os
import sqlite3
import database
import logic
import config
from datetime import datetime, timedelta

def run_backend_tests():
    print("==================================================")
    print("      SMART PANTRY - BACKEND TEST SUITE          ")
    print("==================================================")
    print(f"Test Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("--------------------------------------------------\n")

    # Setup: Reset the database for a clean test environment
    if os.path.exists(config.DB_NAME):
        os.remove(config.DB_NAME)
        
    database.init_db()

    # --- TEST 1: Traffic Light Logic ---
    print("[TEST 1] Testing Traffic Light (Color Coding) Logic")
    today = datetime.now()
    
    expired_date = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    status_red = logic.get_traffic_light_status(expired_date)
    print(f"  - Input: {expired_date} (Expired) -> Result: [{status_red}]")
    assert status_red == "Red"

    expiring_soon_date = (today + timedelta(days=2)).strftime('%Y-%m-%d')
    status_yellow = logic.get_traffic_light_status(expiring_soon_date)
    print(f"  - Input: {expiring_soon_date} (Expiring soon) -> Result: [{status_yellow}]")
    assert status_yellow == "Yellow"

    fresh_date = (today + timedelta(days=10)).strftime('%Y-%m-%d')
    status_green = logic.get_traffic_light_status(fresh_date)
    print(f"  - Input: {fresh_date} (Fresh) -> Result: [{status_green}]")
    assert status_green == "Green"
    print("  -> TEST 1 PASSED\n")

    # --- TEST 2: Smart Product Insertion (Merging) ---
    print("[TEST 2] Testing Smart Product Insertion (Merge Logic)")
    msg1 = logic.add_smart_product("Milk", 2, "2026-12-31", "Dairy")
    print(f"  - Step 1: Add 'Milk' (2x) -> {msg1}")
    
    msg2 = logic.add_smart_product("Milk", 3, "2026-12-31", "Dairy")
    print(f"  - Step 2: Add 'Milk' (3x) again -> {msg2}")
    
    products = database.get_all_products()
    milk = next(p for p in products if p['name'] == "Milk")
    print(f"  - Current state: {milk['name']} quantity is {milk['quantity']}")
    assert milk['quantity'] == 5 
    
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
    
    filtered_app = logic.filter_products(query="app")
    print(f"  - Search for 'app': Found {len(filtered_app)} item(s) ([{filtered_app[0]['name'] if filtered_app else 'None'}])")
    assert len(filtered_app) == 1
    assert filtered_app[0]['name'] == "Apple"
    
    filtered_fruit = logic.filter_products(category="Fruit")
    fruit_names = [p['name'] for p in filtered_fruit]
    print(f"  - Category filter 'Fruit': Found {len(filtered_fruit)} item(s) {fruit_names}")
    assert len(filtered_fruit) == 2
    assert "Apple" in fruit_names and "Orange" in fruit_names
    
    cats = logic.get_unique_categories()
    print(f"  - Unique Categories Found: {cats}")
    assert "Dairy" in cats
    assert "Fruit" in cats
    assert "Snack" in cats
    assert "All" in cats
    print("  -> TEST 3 PASSED\n")

    # --- TEST 4: Statistics Tracking ---
    print("[TEST 4] Testing Stats (Consumed vs. Wasted)")
    milk_id = milk['id']
    
    # Simulate adjusting quantity in UI
    database.update_quantity(milk_id, 3, status="consumed", change_amount=-2)
    print(f"  - Action: Consumed 2 units of Milk.")
    
    database.update_quantity(milk_id, 2, status="wasted", change_amount=-1)
    print(f"  - Action: Wasted 1 unit of Milk.")
    
    stats_str = logic.get_formatted_stats()
    print(f"  - Generated Statistics:\n{stats_str}")
    
    stats = database.get_stats()
    assert stats['consumed'] == 2
    assert stats['wasted'] == 1
    print("  -> TEST 4 PASSED\n")

    # --- TEST 5: Audit Log Tracking ---
    print("[TEST 5] Testing Audit Log (History)")
    
    # Edit the chocolate
    choc = [p for p in database.get_all_products() if p['name'] == "Chocolate"][0]
    logic.edit_smart_product(choc['id'], "Dark Chocolate", 2, "2026-12-31", "Snack")
    print(f"  - Action: Edited 'Chocolate' to 'Dark Chocolate' (qty 2)")
    
    logs = logic.get_audit_history()
    print(f"  - Total Actions Logged: {len(logs)}")
    assert len(logs) > 0
    
    # Last log (descending) is at index 0
    recent_log = logs[0]
    print(f"  - Most Recent Action: [{recent_log['action']}] {recent_log['details']}")
    assert recent_log['action'] == "EDIT"
    print("  -> TEST 5 PASSED\n")

    print("==================================================")
    print("         ALL BACKEND TESTS COMPLETED              ")
    print("==================================================")

if __name__ == "__main__":
    run_backend_tests()
