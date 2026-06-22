# HerdenPilot — Installation

Drei Wege, je nach Gerät und Erfahrung. Für Windows-Einsteiger ist **Variante 1** die einfachste.

---

## Variante 1 — Fertige exe (Windows, am einfachsten)

Keine Installation von Git, Docker oder Python nötig.

1. Geh auf die [Releases-Seite](https://github.com/Glasei81/Tierkalb-/releases)
2. Bei der neuesten Version **`HerdenPilot.exe`** herunterladen
3. Doppelklick auf die Datei
   - Windows zeigt evtl. eine Warnung („Unbekannter Herausgeber"):
     **„Weitere Informationen"** → **„Trotzdem ausführen"** klicken
4. Ein schwarzes Fenster öffnet sich (das ist der Server — **offen lassen**),
   und der Browser startet automatisch mit der App

**Daten:** liegen im Ordner `data` neben der exe — diesen Ordner sichern = Backup.

**Update:** Neue `HerdenPilot.exe` herunterladen und die alte ersetzen. Den `data`-Ordner behalten — alle Tiere und Einträge bleiben erhalten.

**Beenden:** Das schwarze Fenster schließen.

---

## Variante 2 — Mit Git + Docker (Windows/Mac/Linux, für Server-Betrieb)

Geeignet wenn die App dauerhaft laufen soll (z. B. auf einem Mini-PC oder Server).

### Schritt 1 — Git installieren

1. Geh auf [git-scm.com/downloads](https://git-scm.com/downloads)
2. Installer herunterladen und durchklicken (nichts ändern)

### Schritt 2 — Docker Desktop installieren

1. Geh auf [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Installer herunterladen, durchklicken, PC neu starten wenn verlangt
3. Docker Desktop öffnen — warten bis das **grüne Symbol** erscheint

> ⚠️ Falls Docker fragt ob WSL2 installiert werden soll: **Ja** klicken.

### Schritt 3 — App herunterladen und starten

Im Terminal (Windows: „Git Bash", Mac: „Terminal"):

```bash
git clone https://github.com/Glasei81/Tierkalb-.git
cd Tierkalb-
docker compose up -d
```

Dann Browser öffnen: **http://localhost:5000**

### Stoppen / Starten / Updaten

```bash
docker compose down              # Stoppen
docker compose up -d             # Starten
git pull && docker compose up -d --build   # Update
```

Windows-Nutzer können fürs Update auch einfach `update.bat` doppelklicken.

---

## Variante 3 — Zugriff auf eine bestehende Installation (Hauspi)

Wenn HerdenPilot bereits auf einem Raspberry Pi (Hauspi) läuft, brauchst du **gar nichts installieren** — nur Tailscale für den Zugriff.

1. **Tailscale** installieren: [tailscale.com/download](https://tailscale.com/download)
2. Einladungslink vom Betreiber öffnen und mit einem Konto anmelden (Google/GitHub reicht)
3. Browser öffnen — die Adresse bekommst du vom Betreiber:

```
http://100.x.x.x:5000
```

### Tailscale auf dem Hauspi einrichten (nur für den Betreiber)

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Den angezeigten Link im Browser öffnen und anmelden. Danach hat der Hauspi eine feste Tailscale-IP (`100.x.x.x`) und ist von überall erreichbar.

### Kollegen einladen

1. [login.tailscale.com](https://login.tailscale.com) → **Users** → **Invite users**
2. E-Mail-Adresse eingeben — die Person installiert Tailscale, meldet sich an, fertig

---

## Fernzugriff auch für Variante 1 und 2 (Tailscale)

Läuft die App auf deinem eigenen PC, kannst du sie mit Tailscale von überall erreichen:

1. [tailscale.com/download](https://tailscale.com/download) → installieren → anmelden (kostenlos)
2. Die angezeigte IP (`100.x.x.x`) notieren
3. Von jedem Gerät im Tailscale-Netz: `http://100.x.x.x:5000`

---

## Häufige Probleme

**„Port 5000 ist bereits belegt"** (Variante 2)
In `docker-compose.yml` die Zeile `- "5000:5000"` ändern zu `- "5001:5000"`, dann neu starten. App läuft auf `http://localhost:5001`.

**Docker Desktop startet nicht**
Virtualisierung im BIOS aktivieren — Docker zeigt beim Start meist selbst die Lösung an.

**Windows blockiert die exe**
SmartScreen-Warnung: „Weitere Informationen" → „Trotzdem ausführen". Die exe ist nicht signiert, daher die Warnung.

**Der Befehl „docker" wird nicht erkannt**
Docker Desktop ist noch nicht gestartet — öffnen, auf das grüne Symbol warten, nochmal versuchen.

---

## Variante 4 — Online auf Fly.io (für iPad, ohne eigenes Gerät)

Ideal wenn der Kollege kein Windows-PC oder Raspberry Pi haben möchte — die App läuft in der Cloud und ist per URL von jedem Gerät (iPad, iPhone, Android, PC) erreichbar.

**Kosten:** kostenlos (Fly.io Free Tier, 3 GB Speicher, immer online)

### Einmalige Einrichtung (macht der Betreiber, ca. 10 Minuten)

**Schritt 1 — flyctl installieren**

```bash
# Mac/Linux:
curl -L https://fly.io/install.sh | sh

# Windows (PowerShell):
pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**Schritt 2 — Anmelden und App erstellen**

```bash
fly auth login
fly launch --no-deploy
```

Fly.io schlägt einen App-Namen vor (z. B. `herdenpilot-abc123`) — das wird die URL.

**Schritt 3 — Datenspeicher anlegen**

```bash
fly volumes create herdenpilot_data --size 1 --region fra
```

**Schritt 4 — Passwort und Secrets setzen**

```bash
fly secrets set LOGIN_PASSWORD=einSicheresPasswort
fly secrets set SECRET_KEY=$(openssl rand -hex 32)
```

**Schritt 5 — Starten**

```bash
fly deploy
```

Die App ist danach unter `https://APPNAME.fly.dev` erreichbar.

### Kollegen einladen

1. URL mitteilen: `https://APPNAME.fly.dev`
2. Passwort mitteilen (das aus Schritt 4)
3. Fertig — öffnen im Safari auf dem iPad, als PWA zum Homescreen hinzufügen

### Update einspielen

```bash
git pull && fly deploy
```

### Hinweise

- **Abmelden:** Oben rechts in der App → „Abmelden"
- **Daten:** liegen auf dem Fly.io Volume, nicht auf eurem Gerät — regelmäßig CSV exportieren als Backup
- **Ohne Passwort:** Wenn `LOGIN_PASSWORD` nicht gesetzt ist, ist die App ohne Login erreichbar (für lokalen Betrieb hinter Tailscale OK)
