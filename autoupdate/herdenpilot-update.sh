#!/usr/bin/env bash
# HerdenPilot — führt ein angefordertes Update aus.
# Wird von systemd (herdenpilot-update.path/.service) gestartet, sobald
# die App data/update.request anlegt (Telegram /update oder Web-Knopf).

REPO_DIR="${REPO_DIR:-$HOME/Tierkalb-}"
DATA="$REPO_DIR/data"

[ -f "$DATA/update.request" ] || exit 0
mv -f "$DATA/update.request" "$DATA/update.running"

cd "$REPO_DIR" || exit 1
OLD="$(git rev-parse --short HEAD 2>/dev/null || echo '?')"

(
  set -e
  echo "=== HerdenPilot-Update $(date '+%d.%m.%Y %H:%M') ==="
  git pull --ff-only
  if [ "$(git rev-parse --short HEAD)" != "$OLD" ]; then
    docker compose up -d --build
  else
    echo "Bereits auf dem neuesten Stand – kein Neubau nötig."
  fi
) > "$DATA/update.log" 2>&1
RC=$?

NEW="$(git rev-parse --short HEAD 2>/dev/null || echo '?')"
if [ "$RC" -eq 0 ]; then
  printf '%s %s\n' "$OLD" "$NEW" > "$DATA/update.done"
else
  tail -n 20 "$DATA/update.log" > "$DATA/update.failed"
fi
rm -f "$DATA/update.running"
exit 0
