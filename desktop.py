"""
desktop.py — HerdenPilot Desktop-Launcher
Startet den Server lokal und öffnet automatisch den Browser.
Wird für die Windows-exe (PyInstaller) verwendet.
"""
import os
import sys
import threading
import webbrowser

_UPDATE_BAT = r'''@echo off
chcp 65001 >nul
title HerdenPilot aktualisieren
echo ============================================
echo   HerdenPilot wird aktualisiert
echo ============================================
echo.
echo Lade neueste Version herunter...
curl -L -o HerdenPilot_neu.exe "https://github.com/Glasei81/Tierkalb-/releases/latest/download/HerdenPilot.exe"
if not exist HerdenPilot_neu.exe (
    echo.
    echo FEHLER: Download nicht moeglich. Bitte Internetverbindung pruefen.
    echo.
    pause
    exit /b
)
move /Y HerdenPilot_neu.exe HerdenPilot.exe >nul
if errorlevel 1 (
    echo.
    echo FEHLER: HerdenPilot laeuft noch.
    echo Bitte das schwarze HerdenPilot-Fenster schliessen und update.bat erneut starten.
    del HerdenPilot_neu.exe >nul 2>&1
    pause
    exit /b
)
echo.
echo ============================================
echo   Fertig! HerdenPilot ist aktuell.
echo   Deine Daten (Ordner "data") sind unveraendert.
echo ============================================
echo.
echo Du kannst HerdenPilot.exe jetzt wieder starten.
pause
'''


def _ensure_update_bat():
    # Legt update.bat neben der exe an, falls sie noch nicht existiert.
    try:
        path = os.path.join(os.path.dirname(sys.executable), "update.bat")
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(_UPDATE_BAT)
    except Exception:
        pass


if getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(sys.executable))
    _ensure_update_bat()

import database as db
from app import app
from telegram_bot import start_scheduler

if __name__ == "__main__":
    db.init_db()
    start_scheduler(app)
    threading.Timer(1.5, lambda: webbrowser.open("http://localhost:5000")).start()
    print("=" * 50)
    print("HerdenPilot läuft: http://localhost:5000")
    print("Dieses Fenster offen lassen — zum Beenden schließen.")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=False)
