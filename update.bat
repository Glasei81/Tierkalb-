@echo off
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
