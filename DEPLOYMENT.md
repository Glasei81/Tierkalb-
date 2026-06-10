# HerdenPilot — Installation auf Windows

Diese Anleitung führt dich Schritt für Schritt durch die Installation auf einem Windows-PC.
Keine Vorkenntnisse nötig.

---

## Schritt 1 — Git installieren

Git wird gebraucht, um den App-Code herunterzuladen.

1. Geh auf [git-scm.com/downloads](https://git-scm.com/downloads)
2. Klick auf **"Download for Windows"**
3. Installer starten → immer auf **"Next"** klicken, nichts ändern → **"Install"**
4. Nach der Installation auf **"Finish"** klicken

---

## Schritt 2 — Docker Desktop installieren

Docker sorgt dafür, dass die App läuft — ohne Python oder andere Programme manuell installieren zu müssen.

1. Geh auf [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Klick auf **"Download for Windows"**
3. Installer starten → auf **"OK"** bzw. **"Accept"** klicken
4. PC neu starten wenn verlangt
5. **Docker Desktop** öffnen — warten bis unten links ein **grünes Symbol** erscheint

> ⚠️ Falls Docker beim Start fragt ob WSL2 installiert werden soll: **Ja** klicken und warten.

---

## Schritt 3 — App herunterladen

1. Auf dem Desktop Rechtsklick → **"Git Bash Here"** öffnen  
   *(alternativ: Windows-Suche → "Git Bash" eingeben und öffnen)*
2. Diesen Befehl eingeben und mit Enter bestätigen:

```bash
git clone https://github.com/Glasei81/Tierkalb-.git
cd Tierkalb-
```

Es wird ein Ordner `Tierkalb-` erstellt — entweder auf dem Desktop oder im Benutzer-Ordner (`C:\Users\DeinName\Tierkalb-`).

---

## Schritt 4 — App starten

1. App starten:

```bash
docker compose up -d
```

Das dauert beim ersten Mal 1–2 Minuten, weil Docker die App einrichtet.

2. Browser öffnen und folgende Adresse eingeben:

```
http://localhost:5000
```

Es erscheint der **Einrichtungs-Assistent** — Betriebsnamen eingeben, fertig.

---

## Schritt 5 — Tailscale einrichten (Fernzugriff)

Mit Tailscale kannst du die App auch von anderen Geräten aus aufrufen — z. B. vom Handy oder einem anderen PC.

1. Geh auf [tailscale.com/download](https://tailscale.com/download)
2. **"Download for Windows"** klicken und installieren
3. Tailscale öffnen → **"Log in"** mit einem Google- oder GitHub-Konto (kostenlos)
4. Nach dem Login erscheint eine IP-Adresse wie `100.x.x.x` — das ist die Tailscale-IP dieses PCs

Jetzt kann jeder, der ebenfalls Tailscale installiert hat und von dir eingeladen wurde, die App über diese Adresse aufrufen:

```
http://100.x.x.x:5000
```

### Kollegen oder andere Geräte einladen

1. Geh auf [login.tailscale.com](https://login.tailscale.com) → **Users** → **Invite users**
2. E-Mail-Adresse eingeben
3. Die eingeladene Person installiert Tailscale, meldet sich an und kann sofort zugreifen

---

## App stoppen und neu starten

```bash
docker compose down    # Stoppen
docker compose up -d   # Starten
```

---

## Update auf eine neue Version

Entweder im Git Bash:

```bash
cd Tierkalb-
git pull
docker compose up -d --build
```

Oder einfach die Datei **`update.bat`** im Ordner `Tierkalb-` doppelklicken.

---

## Häufige Probleme

**"Port 5000 ist bereits belegt"**  
Ein anderes Programm nutzt Port 5000. In der Datei `docker-compose.yml` im Ordner `Tierkalb-` die Zeile  
`- "5000:5000"` ändern zu `- "5001:5000"`.  
Dann `docker compose up -d --build` eingeben. App läuft danach auf `http://localhost:5001`.

**Docker Desktop startet nicht**  
Virtualisierung ist möglicherweise im BIOS deaktiviert. Beim Start fragt Docker meistens selbst nach und bietet die Lösung an — einfach den Anweisungen auf dem Bildschirm folgen.

**Der Befehl "docker" wird nicht erkannt**  
Docker Desktop ist noch nicht gestartet. Docker Desktop öffnen, warten bis das grüne Symbol erscheint, dann nochmal versuchen.

---

---

# Alternative: Zugriff auf den Hauspi (bestehende Installation)

Wenn HerdenPilot bereits auf einem Raspberry Pi (Hauspi) läuft, brauchst du nichts installieren.
Du greifst einfach über Tailscale auf die laufende App zu.

### Voraussetzungen

- Hauspi läuft bereits mit HerdenPilot
- Tailscale ist auf dem Hauspi installiert
- Du hast eine Einladung ins Tailscale-Netzwerk des Hauspi-Betreibers bekommen

### So richtest du es ein

1. **Tailscale** auf deinem Gerät installieren: [tailscale.com/download](https://tailscale.com/download)
2. Einladungslink aus der E-Mail öffnen und mit einem Konto anmelden
3. Browser öffnen und folgende Adresse eingeben — du bekommst sie vom Betreiber:

```
http://100.x.x.x:5000
```

Fertig — keine weitere Installation nötig.

### Tailscale auf dem Hauspi einrichten (nur für den Betreiber)

Falls Tailscale auf dem Hauspi noch nicht installiert ist:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Es erscheint ein Link im Terminal — diesen im Browser öffnen und mit dem Tailscale-Konto anmelden.
Danach hat der Hauspi eine feste Tailscale-IP (`100.x.x.x`) und ist von überall erreichbar.
