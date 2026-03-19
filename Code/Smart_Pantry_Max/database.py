import sqlite3
import os
from datetime import datetime
import config

def init_db():
    # Erstellt die Tabellen, falls diese noch nicht existieren
    conn = sqlite3.connect(config.DB_NAME)
    with conn:
        # Tabelle für Kategorien
        conn.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        
        # Produkttabelle (Stammdaten)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """)
        
        # Bestandsliste (Transaktionsdaten)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                expiry_date TEXT,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        # Statistik für verbrauchte oder weggeworfene Artikel
        conn.execute("""
            CREATE TABLE IF NOT EXISTS consumption_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER,
                status TEXT CHECK(status IN ('consumed', 'wasted')),
                date TEXT,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        # Audit-Log für die Historie
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT NOT NULL
            )
        """)
        
        # Sicherstellen, dass die Standardkategorie existiert
        conn.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (config.DEFAULT_CATEGORY,))
    conn.close()

def log_audit_action(conn, action, details):
    # Hilfsfunktion zum Erfassen von Historien-Einträgen
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn.execute("INSERT INTO audit_log (timestamp, action, details) VALUES (?, ?, ?)", 
                 (timestamp, action, details))

def add_product(name, quantity, expiry_date, category_name=config.DEFAULT_CATEGORY):
    # Produkt hinzufügen oder Menge bei gleichem Ablaufdatum erhöhen
    if not category_name: category_name = config.DEFAULT_CATEGORY
    
    conn = sqlite3.connect(config.DB_NAME)
    with conn:
        conn.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category_name,))
        category_id = conn.execute("SELECT id FROM categories WHERE name = ?", (category_name,)).fetchone()[0]
        
        conn.execute("INSERT OR IGNORE INTO products (name, category_id) VALUES (?, ?)", (name, category_id))
        product_id = conn.execute("SELECT id FROM products WHERE name = ?", (name,)).fetchone()[0]
        
        existing = conn.execute(
            "SELECT id, quantity FROM inventory WHERE product_id = ? AND expiry_date = ?",
            (product_id, expiry_date)
        ).fetchone()
        
        if existing:
            new_qty = int(existing[1]) + int(quantity)
            conn.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (new_qty, existing[0]))
            log_audit_action(conn, "UPDATE", f"Increased quantity of '{name}' by {quantity} (New total: {new_qty})")
        else:
            conn.execute(
                "INSERT INTO inventory (product_id, quantity, expiry_date) VALUES (?, ?, ?)",
                (product_id, quantity, expiry_date)
            )
            log_audit_action(conn, "ADD", f"Added new item: '{name}' (Qty: {quantity}, Expiry: {expiry_date})")
    conn.close()

def edit_product(item_id, name, quantity, expiry_date, category_name):
    # Das Editieren ändert ein Item komplett
    if not category_name: category_name = config.DEFAULT_CATEGORY
    
    conn = sqlite3.connect(config.DB_NAME)
    with conn:
        # Alte Daten für den Log-Eintrag auslesen
        old_item_query = """
            SELECT p.name, i.quantity, i.expiry_date
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            WHERE i.id = ?
        """
        old_item = conn.execute(old_item_query, (item_id,)).fetchone()
        if not old_item:
            return False, "Item not found"
            
        old_name, old_qty, old_exp = old_item[0], old_item[1], old_item[2]

        conn.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category_name,))
        category_id = conn.execute("SELECT id FROM categories WHERE name = ?", (category_name,)).fetchone()[0]
        
        conn.execute("INSERT OR IGNORE INTO products (name, category_id) VALUES (?, ?)", (name, category_id))
        product_id = conn.execute("SELECT id FROM products WHERE name = ?", (name,)).fetchone()[0]
        
        conn.execute("""
            UPDATE inventory 
            SET product_id = ?, quantity = ?, expiry_date = ? 
            WHERE id = ?
        """, (product_id, quantity, expiry_date, item_id))
        
        log_audit_action(conn, "EDIT", f"Edited Item #{item_id}: '{old_name}' changed to '{name}' (Qty: {quantity}, Exp: {expiry_date})")
    conn.close()
    return True, "Item updated successfully"

def get_all_products():
    # Alle Produkte mit Namen und Kategorien abrufen
    conn = sqlite3.connect(config.DB_NAME)
    conn.row_factory = sqlite3.Row
    query = """
        SELECT i.id, p.name, i.quantity, i.expiry_date, c.name as category
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        JOIN categories c ON p.category_id = c.id
        ORDER BY i.expiry_date ASC
    """
    items = conn.execute(query).fetchall()
    conn.close()
    return items

def delete_product(item_id, status=None):
    # Eintrag löschen und bei Bedarf in Statistik und Log aufnehmen
    conn = sqlite3.connect(config.DB_NAME)
    with conn:
        item_query = "SELECT i.quantity, p.name, i.product_id FROM inventory i JOIN products p ON i.product_id = p.id WHERE i.id = ?"
        item = conn.execute(item_query, (item_id,)).fetchone()
        
        if item:
            qty, name, p_id = item[0], item[1], item[2]
            if status:
                today = datetime.now().strftime('%Y-%m-%d')
                conn.execute(
                    "INSERT INTO consumption_stats (product_id, quantity, status, date) VALUES (?, ?, ?, ?)",
                    (p_id, qty, status, today)
                )
                
            conn.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
            log_audit_action(conn, "DELETE", f"Deleted '{name}' (Qty: {qty}, Reason: {status if status else 'Manual Remove'})")
    conn.close()

def update_quantity(item_id, new_quantity, status=None, change_amount=0):
    # Menge eines Items anpassen
    conn = sqlite3.connect(config.DB_NAME)
    with conn:
        item_query = "SELECT i.quantity, p.name, i.product_id FROM inventory i JOIN products p ON i.product_id = p.id WHERE i.id = ?"
        item = conn.execute(item_query, (item_id,)).fetchone()
        
        if item:
            old_qty, name, p_id = item[0], item[1], item[2]
            
            # Statistische Erfassung bei Reduzierung
            if status and change_amount != 0:
                today = datetime.now().strftime('%Y-%m-%d')
                conn.execute(
                    "INSERT INTO consumption_stats (product_id, quantity, status, date) VALUES (?, ?, ?, ?)",
                    (p_id, abs(change_amount), status, today)
                )

            if new_quantity <= 0:
                conn.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
                log_audit_action(conn, "REMOVE", f"Quantity of '{name}' reached 0. Item removed.")
            else:
                conn.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (new_quantity, item_id))
                log_audit_action(conn, "UPDATE_QTY", f"Changed quantity of '{name}' by {change_amount}. New total: {new_quantity}")
    conn.close()

def get_stats():
    # Daten für die Statistik-Übersicht zusammenstellen
    conn = sqlite3.connect(config.DB_NAME)
    conn.row_factory = sqlite3.Row
    stats = conn.execute("SELECT status, SUM(quantity) as total FROM consumption_stats GROUP BY status").fetchall()
    result = {row['status']: row['total'] for row in stats}
    conn.close()
    return result

def get_audit_log(limit=50):
    # Liefert die Log-Einträge für die Historien-Anzeige
    conn = sqlite3.connect(config.DB_NAME)
    conn.row_factory = sqlite3.Row
    query = "SELECT timestamp, action, details FROM audit_log ORDER BY timestamp DESC, id DESC LIMIT ?"
    logs = conn.execute(query, (limit,)).fetchall()
    conn.close()
    return logs
