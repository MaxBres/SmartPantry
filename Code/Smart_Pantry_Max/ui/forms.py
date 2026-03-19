import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
import logic
from datetime import datetime

class AddProductDialog(ctk.CTkToplevel):
    # Dialogfenster zum Hinzufügen (oder Bearbeiten) eines Produkts
    def __init__(self, parent, item_data=None):
        super().__init__(parent)
        self.item_data = item_data # Wenn hier Daten sind, sind wir im Edit-Modus
        self.is_edit_mode = item_data is not None
        
        title = "Edit Product" if self.is_edit_mode else "Add Product"
        self.title(title)
        self.geometry("400x450")
        
        # Erstellung der UI-Komponenten
        self.create_widgets(title)
        
        if self.is_edit_mode:
            self.populate_data()
            
        # Fokus auf das Dialogfenster setzen
        self.transient(parent)
        self.grab_set()
        self.lift()

    def create_widgets(self, title_text):
        # Spaltenkonfiguration für das Grid-Layout
        self.grid_columnconfigure(1, weight=1)

        # Überschrift des Dialogs
        title_label = ctk.CTkLabel(self, text=title_text, font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10))

        # Eingabefeld für den Produktnamen
        ctk.CTkLabel(self, text="Product Name:").grid(row=1, column=0, padx=20, pady=10, sticky="e")
        self.name_entry = ctk.CTkEntry(self, placeholder_text="e.g., Milk")
        self.name_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        
        # Eingabefeld für die Menge
        ctk.CTkLabel(self, text="Quantity:").grid(row=2, column=0, padx=20, pady=10, sticky="e")
        self.qty_entry = ctk.CTkEntry(self)
        self.qty_entry.insert(0, "1")
        self.qty_entry.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        
        # Eingabefeld für das Ablaufdatum
        ctk.CTkLabel(self, text="Expiry Date\n(YYYY-MM-DD):").grid(row=3, column=0, padx=20, pady=10, sticky="e")
        self.date_entry = ctk.CTkEntry(self, placeholder_text="YYYY-MM-DD")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=3, column=1, padx=20, pady=10, sticky="ew")

        # Eingabefeld für die Kategorie
        ctk.CTkLabel(self, text="Category:").grid(row=4, column=0, padx=20, pady=10, sticky="e")
        self.category_entry = ctk.CTkEntry(self, placeholder_text="e.g., Dairy")
        self.category_entry.grid(row=4, column=1, padx=20, pady=10, sticky="ew")
        
        # Aktions-Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        btn_text = "Update" if self.is_edit_mode else "Save"
        ctk.CTkButton(btn_frame, text=btn_text, command=self.save_product).pack(side=tk.LEFT, padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE")).pack(side=tk.LEFT, padx=10)

    def populate_data(self):
        # Felder mit den existierenden Daten füllen
        # item_data = (id, category, name, quantity, expiry_date, status)
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, self.item_data[2])
        
        self.qty_entry.delete(0, 'end')
        self.qty_entry.insert(0, str(self.item_data[3]))
        
        self.date_entry.delete(0, 'end')
        self.date_entry.insert(0, self.item_data[4])
        
        self.category_entry.delete(0, 'end')
        self.category_entry.insert(0, self.item_data[1])

    def save_product(self):
        # Eingabewerte erfassen
        name = self.name_entry.get().strip()
        qty = self.qty_entry.get().strip()
        date_str = self.date_entry.get().strip()
        category = self.category_entry.get().strip()
        
        # Speichervorgang über die Logik-Ebene
        if self.is_edit_mode:
            item_id = self.item_data[0]
            result = logic.edit_smart_product(item_id, name, qty, date_str, category if category else None)
        else:
            result = logic.add_smart_product(name, qty, date_str, category if category else None)
        
        if result.startswith("Success"):
            messagebox.showinfo("Success", result)
            self.destroy()
        else:
            messagebox.showerror("Error", result)
            self.lift()

class AuditLogDialog(ctk.CTkToplevel):
    # Fenster für die Historie/Audit-Log
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Audit Log / History")
        self.geometry("700x500")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        title = ctk.CTkLabel(self, text="System Activity History", font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, pady=(20, 10))
        
        # Treeview-Tabelle für Logs
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=25, fieldbackground="#343638", borderwidth=0)
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
        
        columns = ("timestamp", "action", "details")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("timestamp", text="Time")
        self.tree.heading("action", text="Action")
        self.tree.heading("details", text="Details")
        
        self.tree.column("timestamp", width=150, anchor="center")
        self.tree.column("action", width=100, anchor="center")
        self.tree.column("details", width=400, anchor="w")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.load_data()
        
        btn = ctk.CTkButton(self, text="Close", command=self.destroy)
        btn.grid(row=2, column=0, pady=20)
        
        self.transient(parent)
        self.grab_set()
        
    def load_data(self):
        logs = logic.get_audit_history()
        for log in logs:
            self.tree.insert("", "end", values=(log['timestamp'], log['action'], log['details']))
