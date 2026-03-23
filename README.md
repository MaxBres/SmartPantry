# 🍏 Smart Pantry

**Smart Pantry** ist eine moderne, auf Python basierende Desktop-Anwendung zur Verwaltung der Vorratskammer. Mit einer benutzerfreundlichen Oberfläche im Dark/Light-Mode hilft die App dabei, Lebensmittelverschwendung zu reduzieren, indem sie den Überblick über Bestände hält, Ablaufdaten überwacht und Statistiken zum Verbrauch liefert.

---

## ✨ Features

- **🚥 Ampelsystem (Traffic Light System):** Automatische farbliche Markierung der Lebensmittel basierend auf dem Ablaufdatum (Grün = Gut, Gelb = Bald ablaufend, Rot = Abgelaufen).
- **📊 Quick Stats Dashboard:** Schnelle Übersicht über die gesamten Artikel, abgelaufene Produkte und einwandfreie Lebensmittel direkt beim Start.
- **🛡️ Audit Log & Historie:** Jede Aktion (Hinzufügen, Bearbeiten, Löschen oder Mengenänderung) wird manipulationssicher in der Datenbank protokolliert.
- **🔍 Suchen & Filtern:** Finde Produkte schnell über die Suchleiste oder filtere sie nach bestimmten Kategorien.
- **🔔 Automatischer Startup Check:** Werden beim Start der App bald ablaufende oder bereits abgelaufene Artikel gefunden, wirst du direkt benachrichtigt.
- **✏️ Schnelle Bearbeitung:** Mengen lassen sich über Quick-Buttons (+/-) anpassen. Alternativ können Namen, Kategorien und Haltbarkeiten komplett editiert werden.
- **📄 Export-Funktion:** Generiere mit einem Klick eine Textdatei (Einkaufsliste/Abgelaufene Artikel) der dringendsten Produkte.
- **📈 Verbrauchs-Statistiken:** Verfolge genau, wie viel Prozent deiner Lebensmittel verbraucht und wie viele weggeworfen wurden.

---

## 🛠️ Technologien & Tech-Stack

- **Sprache:** Python 3.10+
- **GUI-Framework:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (für die moderne Desktop-Oberfläche)
- **Datenbank:** SQLite3 (Lokal und performant, keine externe Serveranbindung nötig)
- **Weitere Libraries:** `darkdetect`, `packaging`, `datetime`

---

## 🚀 Installation & Start

1. **Repository klonen:**
   ```bash
   git clone https://github.com/DEIN_USERNAME/SmartPantry.git
   cd SmartPantry
   ```

2. **Abhängigkeiten installieren:**
   Es wird empfohlen, ein virtuelles Environment (`venv`) zu verwenden.
   ```bash
   pip install -r requirements.txt
   ```

3. **Anwendung starten:**
   ```bash
   python main.py
   ```
   *(Beim ersten Start wird die SQLite-Datenbank `smart_pantry.db` automatisch generiert.)*

---

## 💻 Bedienung

- **Produkte hinzufügen:** Oben im Menü den Namen, die Menge (als Zahl), die Kategorie und das Ablaufdatum (Format: `YYYY-MM-DD`) eingeben und bestätigen.
- **Bestand verwalten:** In der Liste können über die `+` und `-` Buttons die Mengen direkt angepasst werden. Fällt die Menge auf 0, wird das Produkt automatisch in die Verbrauchsstatistik aufgenommen.
- **Bearbeiten:** Über den "Edit"-Button können Name, Kategorie oder Haltbarkeit eines bestehenden Eintrags aktualisiert werden.
- **Historie (Audit Log):** Klicke auf den entsprechenden Button, um eine chronologische Liste aller getätigten Änderungen zu sehen.
- **Statistiken ansehen:** Das Status-Fenster zeigt dir genau an, welche Quote an Lebensmitteln konsumiert oder verschwendet wurde.

---

## 📂 Projektstruktur

```plaintext
Smart_Pantry_Max/
├── ui/                 # Frontend-Komponenten (MainWindow, Forms)
├── database.py         # Datenbank-Management & SQL Queries
├── logic.py            # Business-Logik (Berechnungen, Validierung)
├── config.py           # Globale Konstanten und Einstellungen
├── testing.py          # Unit-Tests für Backend und DB
├── main.py             # Startpunkt der Anwendung
└── requirements.txt    # Python-Abhängigkeiten
```

---
