import database
from ui.main_window import MainWindow

def main():
    # Datenbank am Anfang initialisieren
    database.init_db()
    
    # Hauptfenster der Anwendung starten
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    # Programmstart
    main()