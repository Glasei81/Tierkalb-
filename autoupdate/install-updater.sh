#!/usr/bin/env bash
# Richtet das automatische Update ein (Telegram /update oder Web-Knopf).
# Aufruf im HerdenPilot-Ordner:   sudo bash autoupdate/install-updater.sh
set -e

if [ "$(id -u)" -ne 0 ]; then
  echo "Bitte mit sudo starten:  sudo bash autoupdate/install-updater.sh"
  exit 1
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_USER="$(stat -c %U "$REPO_DIR")"
echo "HerdenPilot-Ordner: $REPO_DIR   (Benutzer: $RUN_USER)"

install -m 755 "$REPO_DIR/autoupdate/herdenpilot-update.sh" /usr/local/bin/herdenpilot-update
sed -e "s|__REPO__|$REPO_DIR|g" -e "s|__USER__|$RUN_USER|g" \
    "$REPO_DIR/autoupdate/herdenpilot-update.service" > /etc/systemd/system/herdenpilot-update.service
sed -e "s|__REPO__|$REPO_DIR|g" \
    "$REPO_DIR/autoupdate/herdenpilot-update.path" > /etc/systemd/system/herdenpilot-update.path

# data-Ordner muss für den Benutzer beschreibbar sein (Docker legt ihn sonst als root an)
mkdir -p "$REPO_DIR/data"
chown "$RUN_USER" "$REPO_DIR/data"

# AUTO_UPDATE=1 in .env setzen
ENV_FILE="$REPO_DIR/.env"
touch "$ENV_FILE"
chown "$RUN_USER" "$ENV_FILE"
if grep -q '^AUTO_UPDATE=' "$ENV_FILE"; then
  sed -i 's/^AUTO_UPDATE=.*/AUTO_UPDATE=1/' "$ENV_FILE"
else
  echo 'AUTO_UPDATE=1' >> "$ENV_FILE"
fi

usermod -aG docker "$RUN_USER" || true

systemctl daemon-reload
systemctl enable --now herdenpilot-update.path

cd "$REPO_DIR"
docker compose up -d --build

echo
echo "✅ Automatisches Update ist eingerichtet."
echo "   Telegram: /update senden"
echo "   Browser:  Einstellungen → Auf Updates prüfen → Jetzt aktualisieren"
