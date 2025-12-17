# Bilder → PDF (A4) – Python GUI

## Übersicht
Dieses Tool ist eine **grafische Python-Anwendung (Tkinter)**, mit der sich mehrere **JPG- und PNG-Bilder** komfortabel zu **einer einzigen A4‑PDF-Datei** zusammenfassen lassen.

Dabei werden die Bilder **nicht abgeschnitten**, sondern sauber auf eine A4‑Seite skaliert und zentriert.

Typische Einsatzfälle:
- Scans als PDF archivieren
- Fotos zu einer PDF zusammenfassen
- Dokumente per Mail versenden

---

## Funktionen

- 📄 **A4‑PDF-Ausgabe** (jede Grafik = eine Seite)
- 🖼️ **JPG & PNG Unterstützung**
- ↕️ **Reihenfolge der Seiten ändern** (hoch / runter)
- 🎚️ **Qualitätsprofile**
  - *Entwurf* (kleine Datei)
  - *Standard* (empfohlen)
  - *Hoch* (maximale Qualität)
- 📐 **Skalierungsmodi**
  - A4 einpassen (hochskalieren)
  - A4 einpassen (nicht hochskalieren)
  - Originalgröße (DPI-basiert)
- 📏 **Rand in Millimetern einstellbar**
- 🔄 **Automatische EXIF-Rotation** (z. B. Handyfotos)
- 🧠 **Transparenzen** werden korrekt behandelt (PNG)

---

## Voraussetzungen

### Betriebssystem
- Windows 10 / 11
- Linux
- macOS

### Python-Version
- **Python 3.9 oder neuer**

Prüfen mit:
```bash
python --version
```

---

## Benötigte Python-Module

Die Anwendung nutzt folgende Bibliotheken:

- `tkinter` (meist bereits enthalten)
- `Pillow`
- `reportlab`

### Installation der Abhängigkeiten

```bash
pip install pillow reportlab
```

Unter Linux (falls tkinter fehlt):
```bash
sudo apt install python3-tk
```

---

## Start der Anwendung

Die Datei heißt zum Beispiel:
```text
img2pdf_gui.py
```

Starten mit:
```bash
python img2pdf_gui.py
```

Danach öffnet sich die grafische Oberfläche.

---

## Bedienung

1. **Hinzufügen…**
   - Bilder (JPG/PNG) auswählen

2. **Reihenfolge festlegen**
   - „Nach oben“ / „Nach unten“

3. **Qualität wählen**
   - Erklärung wird direkt angezeigt

4. **Rand einstellen (optional)**
   - z. B. `10` für 10 mm

5. **Skalierungsmodus wählen**

6. **PDF erzeugen…**
   - Speicherort wählen

---

## Hinweise zur Skalierung

### A4 einpassen (hochskalieren)
- Bild füllt die Seite optimal
- Auch kleinere Bilder werden vergrößert

### A4 einpassen (nicht hochskalieren)
- Kleine Bilder bleiben original groß
- Ideal für Scans

### Originalgröße (DPI)
- Physikalische Größe anhand DPI
- DPI wird aus Bild gelesen oder manuell gesetzt

---

## Typische Probleme

**PDF wirkt unscharf**
- Höhere Qualität auswählen
- DPI-Wert erhöhen

**Bilder stehen auf dem Kopf**
- EXIF-Rotation ist aktiv – Problem sollte nicht auftreten

**Modul fehlt**
```text
ModuleNotFoundError
```
→ Entsprechendes Modul mit `pip install ...` nachinstallieren

---

## Lizenz / Nutzung

- Private und kommerzielle Nutzung möglich
- Keine Garantie oder Haftung

---

## Autor

**Stephan Lauermann**  , AI assisted by ChatCPT
Lauermann IT

---

Viel Spaß beim Nutzen des Tools 🚀

