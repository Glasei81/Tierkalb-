# Tierkalb — Installation & Betrieb

Zwei typische Szenarien: **Kollege auf seinem PC** oder **Zugriff auf deinen Hauspi per Tailscale**.

---

## Voraussetzungen

### Szenario A — Auf einem Windows- oder Mac-PC installieren

Was vorher installiert sein muss:
- **Git** — [git-scm.com/downloads](https://git-scm.com/downloads) (Windows: „Git for Windows“)
- **Docker Desktop** — [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)

Nach der Installation Docker Desktop einmal starten und warten bis das grüne Symbol erscheint.

### Szenario B — Auf deinem Hauspi von außen nutzen (Tailscale)

Was vorher erledigt sein muss:
- Hauspi läuft bereits mit Tierkalb (Docker)
- **Tailscale** auf dem Hauspi installiert (einmalig, siehe unten)
- **Tailscale-App** auf dem Handy oder PC des Kollegen installiert

---

## Szenario A: Frische Installation auf einem PC

Alle Befehle im Terminal eingeben (Windows: „Git Bash“ oder „PowerShell“, Mac: „Terminal“).

**Schritt 1 — Code holen:**
```bash
git clone https://github.com/Glasei81/Tierkalb-.git
cd Tierkalb-
```

**Schritt 2 — App starten:**
```bash
docker compose up -d
```

**Schritt 3 — Browser öffnen:**
```
http://localhost:5000
```

Beim ersten Öffnen erscheint der Einrichtungs-Assistent. Betriebsnamen eingeben — fertig.

---

### Update auf neue Version

```bash
cd Tierkalb-
git pull
docker compose up -d --build
```

Oder einfach doppelklicken:
- **Windows:** `update.bat`
- **Mac/Linux:** `update.sh`

---

### Stoppen / Neustarten

```bash
docker compose down    # Stoppen
docker compose up -d   # Starten
```

---

### Häufige Probleme bei der Installation

**„Port 5000 ist bereits belegt“**  
Ein anderes Programm nutzt Port 5000. Lösung: In `docker-compose.yml` die Zeile  
`- "5000:5000"` ändern auf `- "5001:5000"`, dann `docker compose up -d --build`.  
App läuft dann auf `http://localhost:5001`.

**Docker Desktop startet nicht**  
Windows: Virtualisierung muss im BIOS aktiviert sein. Oder WSL2 installieren (Docker Desktop fragt beim ersten Start danach).

---

## Szenario B: Zugriff auf den Hauspi von überall (Tailscale)

Tailscale baut ein privates VPN zwischen deinen Geräten — ohne Portweiterleitung, ohne feste IP, kostenlos für Privatnutzer.

### Einmalig: Tailscale auf dem Hauspi einrichten

```bash
# Auf dem Hauspi:
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Es erscheint ein Link — diesen im Browser öffnen und mit deinem Tailscale-Konto anmelden (Google/GitHub-Login reicht).

Danach hat der Hauspi eine feste Tailscale-IP (z. B. `100.x.x.x`) und einen Namen (z. B. `hauspi`).

### Kollege einladen

1. Kollege installiert die **Tailscale-App** auf seinem Handy oder PC:  
   [tailscale.com/download](https://tailscale.com/download)
2. Du lädst ihn in dein Tailscale-Netzwerk ein (unter [login.tailscale.com](https://login.tailscale.com) → Users → Invite)
3. Kollege verbindet sich mit Tailscale (einmal tippen reicht)
4. Kollege öffnet im Browser:

```
http://hauspi:5000
```

Das war's. Keine Portweiterleitung, kein DynDNS, kein VPN-Server nötig.

### Nur für dich selbst (ohne Kollegen einladen)

Tailscale auf deinem Handy installieren, mit demselben Konto anmelden, fertig.  
Du erreichst den Hauspi dann von überall über `http://hauspi:5000`.

---

## Datensicherung

Alle Daten liegen in `data/tierkalb.db`. Diese Datei kopieren = Backup.

```bash
# Backup erstellen (auf dem Hauspi):
cp ~/Tierkalb-/data/tierkalb.db ~/Tierkalb-/data/backup_$(date +%Y%m%d).db
```

---

## Telegram einrichten (optional)

Nach der Installation: In der App auf **Menü → Einstellungen** klicken.

**Kurzanleitung:**
1. Telegram öffnen → `@BotFather` suchen → `/newbot` eingeben → Bot-Token kopieren
2. `@userinfobot` suchen → Nachricht schicken → deine Chat-ID kopieren
3. Beides in der App unter Einstellungen eintragen → Speichern
4. „Testnachricht senden“ drücken — klappt es, ist alles richtig

Danach erhältst du täglich um 6:00 Uhr eine Meldung über anstehende Geburten und kannst per Telegram direkt aus dem Stall eintragen.
