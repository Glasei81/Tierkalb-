#!/bin/bash
echo "Tierkalb Update wird gestartet..."
echo

cd "$(dirname "$0")"

echo "Neue Version wird geladen..."
git pull

echo
echo "Container wird neu gebaut..."
docker compose down
docker compose up -d --build

echo
echo "Fertig! Tierkalb laeuft auf http://localhost:5000"
