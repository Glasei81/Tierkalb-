# Tierkalb — Deployment-Anleitung

Hier sind **drei Wege**, wie du Tierkalb bereitstellen kannst.
Dein Kollege braucht am Ende nur einen **Link im Browser** — kein Python, kein Terminal.

---

## Weg 1: Auf deinem Raspberry Pi (Heimnetz) — Empfohlen

Dein Kollege öffnet dann einfach `http://hauspi.local:5000` im Browser.

### Einmalige Installation auf dem Raspberry Pi

```bash
# 1. Code holen
git clone https://github.com/Glasei81/Tierkalb-.git
cd Tierkalb-

# 2. Python-Abhängigkeiten installieren
pip3 install -r requirements.txt

# 3. App starten
python3 app.py
```

Die App läuft jetzt auf **http://hauspi.local:5000**

### App automatisch starten (nach Neustart)

```bash
# Systemd-Service erstellen
sudo nano /etc/systemd/system/tierkalb.service
```

Inhalt:
```ini
[Unit]
Description=Tierkalb Farm-Management
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Tierkalb-
ExecStart=/usr/bin/python3 app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
# Service aktivieren
sudo systemctl enable tierkalb
sudo systemctl start tierkalb
```

---

## Weg 2: Docker (auf jedem PC/Server) — Ein-Befehl-Start

Voraussetzung: [Docker Desktop](https://www.docker.com/products/docker-desktop/) installiert.

```bash
# 1. Code holen
git clone https://github.com/Glasei81/Tierkalb-.git
cd Tierkalb-

# 2. Starten
docker compose up -d
```

Fertig! Die App läuft auf **http://localhost:5000**

Daten bleiben gespeichert auch wenn der Container neu gestartet wird.

```bash
# Stoppen
docker compose down

# Logs ansehen
docker compose logs -f

# Update (neue Version)
git pull
docker compose up -d --build
```

---

## Weg 3: Cloud (Railway.app) — Überall erreichbar

Kostenlos, kein eigener Server nötig. Kollege kann von überall zugreifen.

1. Gehe zu [railway.app](https://railway.app) und melde dich an
2. Klicke **New Project** → **Deploy from GitHub repo**
3. Wähle `Glasei81/Tierkalb-`
4. Railway erkennt automatisch Python/Flask
5. Unter **Variables** setzen:
   - `SECRET_KEY` = ein langes zufälliges Passwort
   - `PORT` = `5000`
6. Klicke **Deploy**

Railway gibt dir eine URL wie `https://tierkalb-xxx.railway.app` — die schickst du dem Kollegen.

> **Hinweis:** Beim kostenlosen Plan läuft die App nach Inaktivität kurz „ein" — üblicherweise innerhalb von 10 Sekunden. Für dauerhaften Betrieb: $5/Monat.

---

## Telegram-Benachrichtigungen einrichten

Nach der Installation: In der App auf **Einstellungen** klicken.

Die App erklärt dort Schritt für Schritt, wie du den Telegram-Bot einrichtest.
Danach erhältst du täglich um 6:00 Uhr eine Meldung über anstehende Geburten.

---

## Datensicherung

Alle Daten liegen in `data/tierkalb.db`. Diese Datei einfach kopieren = Backup.

```bash
# Backup erstellen
cp data/tierkalb.db data/tierkalb_backup_$(date +%Y%m%d).db
```
