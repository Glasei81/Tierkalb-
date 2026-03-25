# 🐄 Tierkalb v2.0 — Farm-Management leicht gemacht

**Tierkalb** ist eine Web-App zum Verwalten deiner Nutztiere (Kühe, Schafe, Schweine, Hühner, etc.). Egal ob Hobby-Landwirt oder Kleinbauer — mit Tierkalb behältst du den Überblick über Trächtigkeit, Kosten und wichtige Termine.

---

## 🚀 Was kann Tierkalb?

✅ **Tiere verwalten** — Namen, Ohrmarken, Geburtsdatum, Rasse eintragen
✅ **Trächtigkeit tracken** — Automatische Berechnung der Geburtstermine
✅ **Kosten dokumentieren** — Tierarzt, Futter, Besamer, etc.
✅ **Telegram-Benachrichtigungen** — Tägliche Updates zu anstehenden Geburten
✅ **Mehrsprachig** — Deutsch & Englisch
✅ **Datensicherheit** — Alles läuft lokal (keine Cloud nötig)

---

## 📋 Installation für Anfänger

### Schritt 1: Vorbereitung (einmalig)

Du brauchst:
- **Computer** mit macOS, Linux oder Windows
- **Python 3.8+** (kostenlos von python.org)
- **GitHub Desktop** oder Git-Kommandozeile (optional, aber empfohlen)

### Schritt 2: Code runterladen

**Option A: Mit GitHub Desktop (einfach)**
1. Lade [GitHub Desktop](https://desktop.github.com) herunter & installiere es
2. Geh auf https://github.com/Glasei81/Tierkalb-
3. Klick **Code** → **Open with GitHub Desktop**
4. Speicher den Ordner auf deinem Computer

**Option B: Mit Terminal/Kommandozeile**
```bash
git clone git@github.com:Glasei81/Tierkalb-.git
cd Tierkalb-
```

### Schritt 3: Abhängigkeiten installieren

Öffne Terminal/Kommandozeile im Tierkalb-Ordner und tippe:

```bash
pip install -r requirements.txt
```

Das installiert automatisch alle nötigen Programme (Flask, SQLite, etc.).

### Schritt 4: App starten

```bash
python app.py
```

Dann öffne deinen Browser und geh zu: **http://localhost:5000**

Fertig! 🎉

---

## 📱 Erste Schritte (in der App)

1. **Setup-Wizard ausführen**
   - Tierart auswählen (Kuh, Schaf, Schwein, Huhn, etc.)
   - Anzahl deiner Tiere eingeben
   - Namen & Ohrmarken speichern

2. **Tier hinzufügen**
   - Klick auf **+ Neues Tier**
   - Gib Namen, Geburtsdatum, Rasse ein
   - Speichern

3. **Trächtigkeit eintragen**
   - Wähle ein Tier aus
   - Klick **Trächtigkeit starten** mit dem Besamerungsdatum
   - Die App berechnet automatisch das Geburtsdatum

4. **Kosten protokollieren**
   - Geh zu **Kosten** → **+ Neue Ausgabe**
   - Wähle Tier & Art (Tierarzt, Futter, etc.)
   - Summe eingeben

5. **Telegram-Bot verbinden** (optional)
   - Gib deinen Bot-Token in der App ein
   - Erhalte täglich Benachrichtigungen

---

## 🔧 Technische Details (für IT-Profis)

### Stack
- **Frontend:** HTML, CSS, JavaScript (mobile-friendly)
- **Backend:** Python + Flask
- **Datenbank:** SQLite (Datei-basiert, keine Server nötig)
- **Integration:** Telegram Bot API

### Dateistruktur
```
Tierkalb-/
├── app.py              # Haupt-App (Flask)
├── database.py         # Datenbank-Logik
├── tierarten.py        # Tierart-Spezifikationen
├── requirements.txt    # Python-Abhängigkeiten
├── templates/          # HTML-Templates
├── static/             # CSS, JavaScript, Bilder
└── data/               # SQLite-Datenbank (lokal)
```

### Datenbank
Die SQLite-Datenbank wird automatisch beim ersten Start erstellt (`data/tierkalb.db`).

### Telegram-Integration
- Erstelle einen Bot via [BotFather](https://t.me/botfather) auf Telegram
- Token in der App eintragen
- Bot sendet täglich um 6:00 Uhr morgens Updates

---

## 🐛 Häufige Probleme

**"Python nicht gefunden"**
→ Python noch nicht installiert? Download: https://python.org

**"Port 5000 schon in Benutzung"**
→ Andere App blockiert Port. Änder in `app.py` Zeile `app.run(port=5000)` zu `app.run(port=5001)`

**"Datenbank-Fehler"**
→ Lösch `data/tierkalb.db` und starte neu. Setup-Wizard wird wieder angezeigt.

**"Telegram funktioniert nicht"**
→ Überprüfe den Bot-Token. Sicherstellen, dass der Bot läuft (`python app.py` muss aktiv sein).

---

## 📧 Support & Entwicklung

Fragen oder Bugs? Erstelle ein Issue auf GitHub oder kontaktier den Entwickler.

---

## 📄 Lizenz

MIT License — siehe LICENSE-Datei für Details.

---

**Viel Spaß mit Tierkalb!** 🚜🐑
