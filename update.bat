@echo off
echo Tierkalb Update wird gestartet...
echo.

cd /d "%~dp0"

echo Neue Version wird geladen...
git pull

echo.
echo Container wird neu gebaut...
docker compose down
docker compose up -d --build

echo.
echo Fertig! Tierkalb laeuft auf http://localhost:5000
echo.
pause
