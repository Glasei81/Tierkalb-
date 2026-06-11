"""
desktop.py — HerdenPilot Desktop-Launcher
Startet den Server lokal und öffnet automatisch den Browser.
Wird für die Windows-exe (PyInstaller) verwendet.
"""

import os
import sys
import threading
import webbrowser

# Datenbank neben der exe ablegen, nicht im Temp-Ordner von PyInstaller
if getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(sys.executable))

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
