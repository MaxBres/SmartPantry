import os

# Basis-Verzeichnis des Projekts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Datenbank-Konfiguration
DB_NAME = os.path.join(BASE_DIR, "smart_pantry.db")

# Standardwerte
DEFAULT_CATEGORY = "General"

# UI-Farben für Treeview-Tags
TAG_RED_BG = "#4a2222"
TAG_YELLOW_BG = "#4a4a22"
TAG_GREEN_BG = "#224a22"

# Statusleisten-Texte
STATUS_READY = "Status: System Ready"
STATUS_UPDATING = "Status: Updating Data..."
STATUS_SAVED = "Status: Changes Saved"
STATUS_DELETED = "Status: Item Deleted"
STATUS_ERROR = "Status: An Error Occurred"
