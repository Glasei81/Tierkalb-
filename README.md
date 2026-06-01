# 🐄 Tierkalb v3.1 — Farm-Management leicht gemacht

**Tierkalb** ist eine Web-App zum Verwalten deiner Nutztiere (Kühe, Schafe, Schweine, Ziegen, Hühner). Egal ob Hobby-Landwirt oder Kleinbauer — mit Tierkalb behältst du den Überblick über Trächtigkeit, Kosten und wichtige Termine.

---

## 🚀 Was kann Tierkalb v3.1?

✅ **Tiere verwalten** — Name, Ohrmarke, Geburtsdatum, Geschlecht, Notizen  
✅ **Ereignisse eintragen** — Brunft, Besamung, Geburt, Impfung, Tierarzt, Sonstiges  
✅ **Trächtigkeit tracken** — Automatische Berechnung der Geburtstermine  
✅ **Kosten dokumentieren** — Tierarzt, Futter, Besamung, Medikamente, Impfung  
✅ **Statistik & Auswertung** — Charts (Kosten/Tier, Kosten/Typ, Monatsverlauf, Besamungsrate)  
✅ **Export** — CSV (Excel-kompatibel) + PDF-Bericht  
✅ **Telegram-Bot** — Status abfragen, Ereignisse eintragen, Tiere anlegen — direkt aus dem Stall  
✅ **PWA** — Als App auf dem Handy-Startbildschirm installierbar  
✅ **Mehrsprachig** — Deutsch & Englisch  
✅ **Docker-ready** — Einfachstes Deployment, läuft auf jedem Rechner/Raspberry Pi  

---

## 🐳 Schnellstart mit Docker (empfohlen)

### Voraussetzungen
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installiert

### Starten

```bash
git clone https://github.com/Glasei81/Tierkalb-.git
cd Tierkalb-
docker compose up -d
```

Browser öffnen: **http://localhost:5000** → Fertig! 🎉

### Stoppen / Neustarten

```bash
docker compose down      # Stoppen (Daten bleiben erhalten)
docker compose up -d     # Wieder starten
```

### Update auf neue Version

**Windows:** `update.bat` doppelklicken  
**Mac/Linux:** `./update.sh` im Terminal ausführen

---

## 📱 Erste Schritte (in der App)

1. **Einrichtungs-Assistent** — Betriebsname eingeben, Sprache wählen → Fertig
2. **Tier anlegen** — „+ Neues Tier“ → Name, Tierart, Ohrmarke, Geburtsdatum
3. **Ereignis eintragen** — Tier anklicken → „Ereignis eintragen“ → Brunft / Besamung / Geburt …
4. **Kosten eintragen** — Tier anklicken → „Kosten eintragen“ → Betrag, Art, Datum
5. **Statistik ansehen** — Menü → Statistik
6. **Telegram einrichten** — Menü → Einstellungen → Token + Chat-ID eintragen

📖 Ausführliche Bedienungsanleitung: **[ANLEITUNG.md](ANLEITUNG.md)**  
🚢 Installation auf PC oder Raspberry Pi: **[DEPLOYMENT.md](DEPLOYMENT.md)**

---

## 📲 Telegram-Befehle

Mit dem Telegram-Bot kannst du **direkt aus dem Stall** eintragen — kein Browser nötig.

### Abfragen
| Befehl | Erklärung |
|--------|----------|
| `/status` | Vollständiger Überblick: Brunft, Trächtigkeit, bevorstehende Geburten |
| `/tiere` | Liste aller aktiven Tiere |
| `/hilfe` | Befehlsliste |

### Tiere anlegen
| Befehl | Beispiel | Erklärung |
|--------|----------|----------|
| `/neues_tier` | `/neues_tier Emma Rind` | Neue Kuh „Emma“ anlegen |
| `/neues_tier` | `/neues_tier Wolke Schaf` | Neues Schaf „Wolke“ anlegen |

### Ereignisse & Kosten eintragen
| Befehl | Beispiel | Erklärung |
|--------|----------|----------|
| `/besamung` | `/besamung Emma` | Besamung heute |
| `/besamung` | `/besamung Emma 24.05.` | Besamung mit Datum |
| `/brunft` | `/brunft Bella` | Brunft heute |
| `/geburt` | `/geburt Lisa 20.05.` | Geburt mit Datum |
| `/impfung` | `/impfung Anna` | Impfung heute |
| `/tierarzt` | `/tierarzt Emma 150` | Tierarzt 150 € |
| `/kosten` | `/kosten Emma 80` | Sonstige Kosten 80 € |

Täglich um **6:00 Uhr** kommt automatisch eine Meldung, wenn Geburten bevorstehen.

---

## 🔧 Technische Details

### Stack
- **Backend:** Python 3.11 + Flask
- **Datenbank:** SQLite (dateibasiert, kein Datenbankserver nötig)
- **Frontend:** Bootstrap 5.3, Chart.js
- **Export:** ReportLab (PDF), csv (Excel)
- **Telegram:** APScheduler + Polling-Thread
- **Deployment:** Docker / docker-compose

### Tragzeiten (voreingestellt)
| Tierart | Tragzeit | Brunft-Zyklus |
|---------|----------|---------------|
| 🐄 Rinder | 280 Tage | 21 Tage |
| 🐑 Schafe | 150 Tage | 17 Tage |
| 🐷 Schweine | 114 Tage | 21 Tage |
| 🐐 Ziegen | 150 Tage | 21 Tage |
| 🐔 Hühner | 21 Tage (Brutzeit) | — |

---

## 🐛 Häufige Probleme

**Port 5000 schon belegt**  
→ In `docker-compose.yml` den Port ändern: `"5001:5000"`

**Datenbank-Fehler nach Update**  
→ `docker compose down && docker compose up -d --build`

**Telegram antwortet nicht**  
→ Token und Chat-ID unter Menü → Einstellungen prüfen. Einmal `/start` an den Bot schicken. Testnachricht-Button verwenden.

---

## 📧 Support

Fragen oder Bugs → [GitHub Issues](https://github.com/Glasei81/Tierkalb-/issues)  
Entwickler unterstützen → Menü → ❤️

---

**Viel Erfolg am Betrieb!** 🚜🐄🐑
