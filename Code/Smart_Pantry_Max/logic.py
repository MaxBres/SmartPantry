from datetime import datetime
import database

def get_traffic_light_status(expiry_date_str):
    try:
        today = datetime.now().date()
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
        delta = (expiry_date - today).days
        
        if delta < 0:
            return "Red"
        elif delta <= 3:
            return "Yellow"
        else:
            return "Green"
    except Exception:
        return "Unknown"

def validate_product_data(name, quantity, expiry_date):
    # Hilfsfunktion, um Duplizierten Code zu vermeiden
    if not name:
        return False, "Error: Name cannot be empty"
    try:
        qty = int(quantity)
        if qty <= 0:
            return False, "Error: Quantity must be positive"
    except ValueError:
        return False, "Error: Quantity must be a number"
    
    try:
        datetime.strptime(expiry_date, '%Y-%m-%d')
    except ValueError:
        return False, "Error: Invalid date format (YYYY-MM-DD)"
        
    return True, int(quantity)

def add_smart_product(name, quantity, expiry_date, category=None):
    valid, result = validate_product_data(name, quantity, expiry_date)
    if not valid:
        return result
    
    database.add_product(name, result, expiry_date, category)
    return f"Success: Added/Updated {name}"

def edit_smart_product(item_id, name, quantity, expiry_date, category=None):
    # Logik-Funktion zum Bearbeiten eines Produkts
    valid, result = validate_product_data(name, quantity, expiry_date)
    if not valid:
        return result
        
    success, msg = database.edit_product(item_id, name, result, expiry_date, category)
    if success:
        return f"Success: Item updated"
    return f"Error: {msg}"

def filter_products(query="", category="All"):
    products = database.get_all_products()
    filtered = []
    
    for p in products:
        name_match = query.lower() in p['name'].lower()
        cat_p = p['category']
        category_match = (category == "All" or category == cat_p)
        
        if name_match and category_match:
            filtered.append(p)
            
    return filtered

def get_unique_categories():
    products = database.get_all_products()
    categories = {"All"}
    for p in products:
        categories.add(p['category'])
    return sorted(list(categories))

def get_expiring_products_for_export():
    products = database.get_all_products()
    expiring = []
    for p in products:
        status = get_traffic_light_status(p['expiry_date'])
        if status in ["Red", "Yellow"]:
            expiring.append(p)
    return expiring

def check_startup_alerts():
    # Prüft beim Start, ob Produkte abgelaufen sind oder bald ablaufen
    products = database.get_all_products()
    expired = 0
    expiring_soon = 0
    
    for p in products:
        status = get_traffic_light_status(p['expiry_date'])
        if status == "Red":
            expired += 1
        elif status == "Yellow":
            expiring_soon += 1
            
    alerts = []
    if expired > 0:
        alerts.append(f"{expired} item(s) have expired!")
    if expiring_soon > 0:
        alerts.append(f"{expiring_soon} item(s) are expiring within 3 days.")
        
    return alerts

def get_quick_stats():
    # Berechnet die Daten für das Dashboard
    products = database.get_all_products()
    total_items = sum(p['quantity'] for p in products)
    
    expired = sum(p['quantity'] for p in products if get_traffic_light_status(p['expiry_date']) == "Red")
    good = sum(p['quantity'] for p in products if get_traffic_light_status(p['expiry_date']) == "Green")
    
    return {
        "total": total_items,
        "expired": expired,
        "good": good
    }

def export_to_text(filepath):
    expiring = get_expiring_products_for_export()
    if not expiring:
        return False, "No expired or expiring items found."
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("--- SHOPPING LIST / EXPIRED ITEMS ---\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for p in expiring:
                status = get_traffic_light_status(p['expiry_date'])
                cat = p['category'] if p['category'] else "General"
                f.write(f"[{status}] {p['name']} ({p['quantity']}x) - Expiry: {p['expiry_date']} - Cat: {cat}\n")
        return True, f"Successfully exported {len(expiring)} items."
    except Exception as e:
        return False, str(e)

def get_formatted_stats():
    stats = database.get_stats()
    consumed = stats.get('consumed', 0)
    wasted = stats.get('wasted', 0)
    total = consumed + wasted
    
    if total == 0:
        return "No data recorded yet."
    
    waste_percentage = (wasted / total) * 100
    return (f"Total Items Tracked: {total}\n"
            f"✅ Consumed: {consumed}\n"
            f"🗑️ Wasted: {wasted}\n"
            f"Waste Rate: {waste_percentage:.1f}%")

def get_audit_history():
    # Logik-Ebene Aufruf für Historie
    return database.get_audit_log()
