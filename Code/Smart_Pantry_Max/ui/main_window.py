import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import database
import logic
import config
from ui.forms import AddProductDialog, AuditLogDialog

# Grundeinstellungen für das Erscheinungsbild
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart Pantry Manager")
        self.geometry("1100x750")

        # Konfiguration des Grid-Layouts
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # UI-Komponenten aufbauen
        self.create_sidebar()
        self.create_main_area()
        self.create_status_bar()
        
        # Initiale Prüfungen und Datenladung
        self.refresh_data()
        self.check_startup_alerts() # Warnt vor abgelaufenen Produkten

    def check_startup_alerts(self):
        # Zeigt ein Popup, wenn beim Starten Dinge abgelaufen sind
        alerts = logic.check_startup_alerts()
        if alerts:
            msg = "\n".join(alerts)
            messagebox.showwarning("Pantry Alerts (Startup Check)", msg)

    def set_status(self, text):
        # Hilfsfunktion für die Statusleiste
        self.status_label.configure(text=text)
        
    def create_sidebar(self):
        # Seitenleiste für Navigation und Aktionen
        self.sidebar_frame = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", rowspan=2) # Rowspan, damit Statusbar rechts bleibt
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Smart Pantry", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 20))

        # Buttons für die Bestandsverwaltung
        self.btn_add = ctk.CTkButton(self.sidebar_frame, text="Add New Item", command=self.open_add_dialog)
        self.btn_add.grid(row=1, column=0, padx=20, pady=10)

        self.btn_edit = ctk.CTkButton(self.sidebar_frame, text="Edit Selected", command=self.open_edit_dialog, 
                                      fg_color="#D4AC0D", hover_color="#B7950B", text_color="black")
        self.btn_edit.grid(row=2, column=0, padx=20, pady=10)

        self.btn_delete = ctk.CTkButton(self.sidebar_frame, text="Delete Selected", command=self.delete_selected, 
                                      fg_color="#A12D2D", hover_color="#822323")
        self.btn_delete.grid(row=3, column=0, padx=20, pady=10)

        self.btn_plus = ctk.CTkButton(self.sidebar_frame, text="Quantity +1", command=lambda: self.adjust_quantity(1),
                                     fg_color="transparent", border_width=2)
        self.btn_plus.grid(row=4, column=0, padx=20, pady=10)

        self.btn_minus = ctk.CTkButton(self.sidebar_frame, text="Quantity -1", command=lambda: self.adjust_quantity(-1),
                                      fg_color="transparent", border_width=2)
        self.btn_minus.grid(row=5, column=0, padx=20, pady=10)

        # Erweiterte Funktionen
        self.btn_history = ctk.CTkButton(self.sidebar_frame, text="View History Log", command=self.show_history, 
                                         fg_color="#1F618D", hover_color="#1A5276")
        self.btn_history.grid(row=6, column=0, padx=20, pady=20)

        self.btn_stats = ctk.CTkButton(self.sidebar_frame, text="View Statistics", command=self.show_statistics,
                                      fg_color="#2D5A27", hover_color="#21421D")
        self.btn_stats.grid(row=7, column=0, padx=20, pady=10)

        self.btn_export = ctk.CTkButton(self.sidebar_frame, text="Export List", command=self.export_list,
                                       fg_color="#5D6D7E", hover_color="#34495E")
        self.btn_export.grid(row=8, column=0, padx=20, pady=10)

        # Auswahl des Design-Modus
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Design Mode:", anchor="w")
        self.appearance_mode_label.grid(row=11, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                               command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=12, column=0, padx=20, pady=(10, 20))

    def create_main_area(self):
        # Hauptbereich mit Dashboard, Suchfeld und Artikeltabelle
        self.main_container = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.main_container.grid(row=0, column=1, padx=20, pady=(20, 0), sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(2, weight=1)

        # Quick Stats Dashboard
        self.dashboard_frame = ctk.CTkFrame(self.main_container, height=80)
        self.dashboard_frame.grid(row=0, column=0, pady=(0, 10), sticky="ew")
        self.dashboard_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Labels für Quick Stats
        self.lbl_stat_total = ctk.CTkLabel(self.dashboard_frame, text="Total Items: 0", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_stat_total.grid(row=0, column=0, pady=20)
        
        self.lbl_stat_good = ctk.CTkLabel(self.dashboard_frame, text="Fresh: 0", font=ctk.CTkFont(size=16, weight="bold"), text_color="#2ECC71")
        self.lbl_stat_good.grid(row=0, column=1, pady=20)
        
        self.lbl_stat_expired = ctk.CTkLabel(self.dashboard_frame, text="Expired: 0", font=ctk.CTkFont(size=16, weight="bold"), text_color="#E74C3C")
        self.lbl_stat_expired.grid(row=0, column=2, pady=20)

        # Bereich für Suchen und Filtern
        self.filter_frame = ctk.CTkFrame(self.main_container)
        self.filter_frame.grid(row=1, column=0, pady=(0, 10), sticky="ew")
        self.filter_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.filter_frame, text="Search:").grid(row=0, column=0, padx=10, pady=10)
        self.search_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="Type product name...")
        self.search_entry.grid(row=0, column=1, sticky="ew", pady=10)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_data())

        ctk.CTkLabel(self.filter_frame, text="Category:").grid(row=0, column=2, padx=10, pady=10)
        self.category_var = tk.StringVar(value="All")
        self.category_filter = ctk.CTkOptionMenu(self.filter_frame, variable=self.category_var, 
                                                 values=["All"], command=lambda v: self.refresh_data())
        self.category_filter.grid(row=0, column=3, padx=10, pady=10)

        # Darstellung der Artikel in einer Tabelle (Treeview)
        self.table_frame = ctk.CTkFrame(self.main_container)
        self.table_frame.grid(row=2, column=0, sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)

        # Styling der Tabellenansicht
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=30, fieldbackground="#343638", borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")
        
        columns = ("id", "category", "name", "quantity", "expiry_date", "status")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="extended")
        
        # Festlegen der Spaltenüberschriften
        self.tree.heading("id", text="ID")
        self.tree.heading("category", text="Category")
        self.tree.heading("name", text="Product Name")
        self.tree.heading("quantity", text="Qty")
        self.tree.heading("expiry_date", text="Expiry Date")
        self.tree.heading("status", text="Status")
        
        # Definition der Spaltenbreiten
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("category", width=120, anchor="w")
        self.tree.column("name", width=250, anchor="w")
        self.tree.column("quantity", width=80, anchor="center")
        self.tree.column("expiry_date", width=120, anchor="center")
        self.tree.column("status", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=10)

        # Tags für die farbliche Kennzeichnung (Ampelsystem) über Config
        self.tree.tag_configure("Red", background=config.TAG_RED_BG, foreground="white")
        self.tree.tag_configure("Yellow", background=config.TAG_YELLOW_BG, foreground="white")
        self.tree.tag_configure("Green", background=config.TAG_GREEN_BG, foreground="white")

    def create_status_bar(self):
        # Bottom Bar: Statusanzeige
        self.status_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.status_frame.grid(row=1, column=1, sticky="ew")
        self.status_frame.grid_propagate(False)
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(self.status_frame, text=config.STATUS_READY, anchor="w")
        self.status_label.grid(row=0, column=0, padx=10, pady=2, sticky="w")

    def update_dashboard(self):
        # Aktualisiert die Dashboard-Kacheln
        stats = logic.get_quick_stats()
        self.lbl_stat_total.configure(text=f"Total Items: {stats['total']}")
        self.lbl_stat_good.configure(text=f"Fresh: {stats['good']}")
        self.lbl_stat_expired.configure(text=f"Expired: {stats['expired']}")

    def refresh_data(self):
        # Zeige Aktivitätsstatus an
        self.set_status(config.STATUS_UPDATING)
        
        # Aktualisierung der Kategorien im Filter-Menü
        cats = logic.get_unique_categories()
        current_val = self.category_var.get()
        self.category_filter.configure(values=cats)
        if current_val not in cats:
            self.category_var.set("All")

        # Tabelle komplett leeren vor Neuaufbau
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Gefilterte Daten basierend auf Suche und Kategorie laden
        query = self.search_entry.get()
        cat = self.category_var.get()
        products = logic.filter_products(query, cat)
        
        # Einträge in die Tabelle einfügen
        for p in products:
            status = logic.get_traffic_light_status(p['expiry_date'])
            self.tree.insert("", "end", values=(
                p['id'],
                p['category'],
                p['name'],
                p['quantity'],
                p['expiry_date'],
                status
            ), tags=(status,))
            
        # Dashboard-Werte aktualisieren
        self.update_dashboard()
        # Status zurücksetzen
        self.set_status(config.STATUS_READY)

    def open_add_dialog(self):
        # Öffnet das Fenster für die Artikeleingabe
        dialog = AddProductDialog(self)
        self.wait_window(dialog)
        self.refresh_data()
        self.set_status(config.STATUS_SAVED)
        
    def open_edit_dialog(self):
        # Öffnet das Fenster zur Artikelbearbeitung für den selektierten Eintrag
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Select an item to edit.")
            return
        if len(selected_items) > 1:
            messagebox.showwarning("Warning", "Please select only one item to edit.")
            return
            
        item_id = selected_items[0]
        vals = self.tree.item(item_id, 'values')
        
        # vals wird an den Dialog übergeben (Edit Mode)
        dialog = AddProductDialog(self, item_data=vals)
        self.wait_window(dialog)
        self.refresh_data()
        self.set_status(config.STATUS_SAVED)

    def delete_selected(self):
        # Löschen der markierten Artikel
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Select an item to delete.")
            return
            
        # Grund für die Entfernung abfragen
        status = self.ask_consumption_status("Delete Item", "Was this item consumed or wasted?")
        if not status: return 

        if messagebox.askyesno("Confirm", f"Delete {len(selected_items)} item(s)?"):
            for item_id in selected_items:
                p_id = self.tree.item(item_id, 'values')[0]
                database.delete_product(p_id, status=status)
            self.refresh_data()
            self.set_status(config.STATUS_DELETED)

    def adjust_quantity(self, change):
        # Mengenanpassung der markierten Artikel
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Select an item to adjust quantity.")
            return
            
        status = None
        if change < 0:
            # Bei Verringerung nach dem Grund fragen (Statistik)
            status = self.ask_consumption_status("Decrease Quantity", "Was the removed item consumed or wasted?")
            if not status: return

        for item_id in selected_items:
            vals = list(self.tree.item(item_id, 'values'))
            p_id = vals[0]
            current_qty = int(vals[3])
            new_qty = current_qty + change
            database.update_quantity(p_id, new_qty, status=status, change_amount=change)
        self.refresh_data()
        self.set_status(config.STATUS_SAVED)

    def show_history(self):
        # Zeigt das Audit-Log an
        dialog = AuditLogDialog(self)
        self.wait_window(dialog)

    def ask_consumption_status(self, title, message):
        # Aufruf des Status-Dialogs (Consumed/Wasted)
        dialog = StatusDialog(self, title, message)
        self.wait_window(dialog)
        return dialog.result

    def export_list(self):
        # Bestand als Textdatei für den Einkauf exportieren
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                                 filetypes=[("Text files", "*.txt")],
                                                 initialfile="Shopping_List.txt")
        if file_path:
            success, msg = logic.export_to_text(file_path)
            if success:
                messagebox.showinfo("Export", msg)
                self.set_status("Status: List exported")
            else:
                messagebox.showerror("Export Error", msg)
                self.set_status(config.STATUS_ERROR)

    def show_statistics(self):
        # Anzeige der Verbrauchsstatistik in einer Box
        stats_text = logic.get_formatted_stats()
        messagebox.showinfo("Pantry Statistics", stats_text)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        # Wechsel zwischen Light/Dark Mode
        ctk.set_appearance_mode(new_appearance_mode)

class StatusDialog(ctk.CTkToplevel):
    # Eigener Dialog zur Statusabfrage beim Verbrauchen/Löschen
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x150")
        self.result = None
        
        self.label = ctk.CTkLabel(self, text=message, wraplength=250)
        self.label.pack(pady=20)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20)
        
        # Entscheidungsschaltflächen für Statistikdaten
        ctk.CTkButton(btn_frame, text="Consumed", fg_color="green", width=100,
                      command=lambda: self.set_result("consumed")).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Wasted", fg_color="red", width=100,
                      command=lambda: self.set_result("wasted")).pack(side="right", padx=5)
        
        self.transient(parent)
        self.grab_set()

    def set_result(self, res):
        self.result = res
        self.destroy()
