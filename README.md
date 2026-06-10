# HerdenPilot — Herdenmanagement ohne teure Lizenzen

**Volle Kontrolle über deine Herde — läuft lokal auf deinem Betrieb, kostet nichts.**

HerdenPilot ist eine Web-App für Landwirte, die professionelles Herdenmanagement wollen, ohne monatliche Abo-Gebühren oder teure Softwarelizenzen. Alle Daten bleiben bei dir — kein Cloud-Zwang, kein Vendor Lock-in. Läuft auf jedem PC oder Raspberry Pi, bedienbar über den Browser — auch am Handy.

---

## Was kann HerdenPilot?

✅ **Tiere verwalten** — Name, Ohrmarke, Geburtsdatum, Geschlecht, Notizen  
✅ **Ereignisse eintragen** — Brunft, Besamung, Geburt, Impfung, Tierarzt, Sonstiges  
✅ **Trächtigkeiten tracken** — Automatische Berechnung der Geburtstermine  
✅ **Kosten dokumentieren** — Tierarzt, Futter, Besamung, Medikamente, Impfung  
✅ **Statistik & Auswertung** — Charts, Kostenübersichten, Besamungsrate, Kosten pro Geburt  
✅ **Export** — CSV (Excel-kompatibel) + PDF-Bericht  
✅ **Telegram-Bot** — Status abfragen, Ereignisse eintragen — direkt aus dem Stall  
✅ **PWA** — Als App auf dem Handy-Startbildschirm installierbar  
✅ **Mehrsprachig** — Deutsch & Englisch  
✅ **Docker-ready** — Läuft auf jedem PC oder Raspberry Pi  

---

## Schnellstart

### Voraussetzungen
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installiert

### Starten

```bash
git clone https://github.com/Glasei81/Tierkalb-.git
cd Tierkalb-
docker compose up -d
```

Browser öffnen: **http://localhost:5000** → Fertig!

### Update auf neue Version

```bash
git pull && docker compose up -d --build
```

Windows-Nutzer: `update.bat` doppelklicken.

📖 Ausführliche Installationsanleitung: **[DEPLOYMENT.md](DEPLOYMENT.md)**  
📖 Bedienungsanleitung: **[ANLEITUNG.md](ANLEITUNG.md)**

---

## Telegram-Bot

Mit dem Bot kannst du **direkt aus dem Stall** eintragen — kein Browser nötig.

| Befehl | Erklärung |
|--------|----------|
| `/status` | Brunft, Trächtigkeit, bevorstehende Geburten |
| `/tiere` | Liste aller aktiven Tiere |
| `/besamung Emma` | Besamung heute eintragen |
| `/brunft Bella` | Brunft heute eintragen |
| `/geburt Lisa` | Geburt heute eintragen |
| `/impfung Anna` | Impfung heute eintragen |
| `/tierarzt Emma 150` | Tierarzt 150 € eintragen |
| `/hilfe` | Alle Befehle |

Täglich um **6:00 Uhr** kommt automatisch eine Meldung bei bevorstehenden Geburten, fälligen Trächtigkeitskontrollen und Impfungen.

---

## Technische Details

| | |
|---|---|
| **Backend** | Python 3.11 + Flask |
| **Datenbank** | SQLite (keine Serverinstallation nötig) |
| **Frontend** | Bootstrap 5.3, Chart.js |
| **Export** | ReportLab (PDF), CSV |
| **Telegram** | APScheduler + Polling-Thread |
| **Deployment** | Docker / docker-compose |

### Tragzeiten & Brunft-Zyklen

| Tierart | Tragzeit | Brunft-Zyklus |
|---------|----------|---------------|
| 🐄 Rinder | 280 Tage | 21 Tage |
| 🐑 Schafe | 150 Tage | 17 Tage |
| 🐷 Schweine | 114 Tage | 21 Tage |
| 🐐 Ziegen | 150 Tage | 21 Tage |

---

## Häufige Probleme

**Port 5000 belegt** → In `docker-compose.yml` ändern: `- "5001:5000"`  
**Docker startet nicht** → Docker Desktop öffnen, auf grünes Symbol warten  
**Telegram antwortet nicht** → Token + Chat-ID unter Einstellungen prüfen, `/start` schicken

---

**Viel Erfolg am Betrieb!** 🚜
