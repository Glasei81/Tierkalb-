#!/usr/bin/env bash
# HerdenPilot — Einrichtung auf einem frischen Raspberry Pi (oder Debian/Ubuntu)
# Aufruf:  curl -fsSL https://raw.githubusercontent.com/Glasei81/Tierkalb-/main/setup-pi.sh | bash
set -e

REPO_URL="https://github.com/Glasei81/Tierkalb-.git"
TARGET="$HOME/Tierkalb-"

echo "============================================"
echo "  HerdenPilot wird eingerichtet"
echo "============================================"

echo "→ Systempakete aktualisieren …"
sudo apt-get update -y
sudo apt-get install -y git curl

if ! command -v docker >/dev/null 2>&1; then
  echo "→ Docker installieren …"
  curl -fsSL https://get.docker.com | sudo sh
fi
sudo usermod -aG docker "$USER" || true

if [ -d "$TARGET/.git" ]; then
  echo "→ HerdenPilot ist schon vorhanden – hole neuesten Stand …"
  git -C "$TARGET" pull --ff-only
else
  echo "→ HerdenPilot herunterladen …"
  git clone "$REPO_URL" "$TARGET"
fi
cd "$TARGET"
[ -f .env ] || cp .env.example .env
mkdir -p data

echo "→ HerdenPilot bauen und starten (beim ersten Mal einige Minuten) …"
sudo docker compose up -d --build

echo "→ Automatisches Update einrichten …"
sudo bash autoupdate/install-updater.sh

if ! command -v tailscale >/dev/null 2>&1; then
  printf "Tailscale für den Fernzugriff installieren? [j/N] "
  read -r ANTWORT < /dev/tty || ANTWORT="n"
  case "$ANTWORT" in
    j|J|y|Y)
      curl -fsSL https://tailscale.com/install.sh | sh
      sudo tailscale up
      ;;
  esac
fi

IP="$(hostname -I | awk '{print $1}')"
echo
echo "============================================"
echo "  ✅ Fertig!"
echo "  Im Browser öffnen:  http://$IP:5000"
echo "  Updates:            in Telegram /update senden"
echo "============================================"
