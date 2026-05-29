# Tierkalb — Bedienungsanleitung

**Für den täglichen Gebrauch am Betrieb**

---

## Inhalt

1. [App öffnen](#1-app-öffnen)
2. [Erste Einrichtung](#2-erste-einrichtung)
3. [Tier anlegen](#3-tier-anlegen)
4. [Ereignis eintragen](#4-ereignis-eintragen) — Brunft, Besamung, Geburt
5. [Kosten eintragen](#5-kosten-eintragen)
6. [Statistik & Auswertung](#6-statistik--auswertung)
7. [Export: CSV & PDF](#7-export-csv--pdf)
8. [Telegram-Befehle](#8-telegram-befehle)
9. [Häufige Fragen](#9-häufige-fragen)

---

## 1. App öffnen

Die App läuft im Browser — wie eine normale Webseite.
Du brauchst **keine Installation**, kein App-Store.

**Am Handy oder Computer:**
Link im Browser öffnen (du hast ihn per WhatsApp bekommen).

**Tipp:** Den Link als Lesezeichen speichern oder auf dem Handy-Startbildschirm ablegen:
- iPhone: Safari → Teilen-Symbol → „Zum Home-Bildschirm“
- Android: Chrome → Menü (⋮) → „Zum Startbildschirm hinzufügen“

Dann hast du ein Symbol wie eine echte App.

---

## 2. Erste Einrichtung

Beim allerersten Öffnen erscheint der **Einrichtungs-Assistent**.

1. **Betriebsname** eingeben (z.B. „Hof Mustermann“)
2. **Deinen Namen** eingeben (optional)
3. **Sprache** wählen: Deutsch oder Englisch
4. Auf **„Betrieb erstellen“** drücken

Die Tierarten (Rinder, Schafe, Schweine, Ziegen, Hühner) sind bereits voreingestellt.

**Fertig** — du bist auf dem Dashboard.

---

## 3. Tier anlegen

**So geht's:**

1. Auf dem Dashboard oben rechts auf **„+ Neues Tier“** drücken
2. Felder ausfüllen:

| Feld | Erklärung | Pflicht? |
|------|-----------|----------|
| **Name** | Freiname, z.B. „Emma“ | Ja |
| **Ohrmarke** | Amtliche Nummer, z.B. AT 123456789 | Nein |
| **Tierart** | Rind, Schaf, Schwein … | Empfohlen |
| **Geschlecht** | Weiblich / Männlich | Nein |
| **Geburtsdatum** | Eigenes Geburtsdatum des Tieres | Nein |
| **Notiz** | Interne Anmerkung | Nein |

3. Auf **„Speichern“** drücken

Das Tier erscheint jetzt auf dem Dashboard.

**Tier bearbeiten:** Auf den Namen klicken → „Bearbeiten“

**Tier archivieren:** Auf den Namen klicken → „Archivieren“
(Das Tier wird nicht gelöscht, nur ausgeblendet — Daten bleiben erhalten.)

---

## 4. Ereignis eintragen

Ereignisse sind alles, was mit dem Tier passiert: Brunft, Besamung, Geburt, Impfung, Tierarztbesuch.

**So geht's:**

1. Auf dem Dashboard auf den **Tiernamen** klicken
2. Im Bereich „Ereignisse“ rechts oben auf **„+ Eintragen“** drücken
3. **Ereignis-Typ** auswählen:
   - 🌸 **Brunft** — Tier ist stierig
   - 💉 **Besamung** — Tier wurde besamt (Künstliche Besamung oder Decken)
   - 🐣 **Geburt** — Tier hat gekalbt/gelammt
   - 💊 **Impfung** — Impfung durchgeführt
   - 🩺 **Tierarzt** — Tierarztbesuch
4. **Datum** eintragen (Standard: heute)
5. **Notiz** hinzufügen (optional, z.B. KB-Stier, Diagnose)
6. Auf **„Speichern“** drücken

**Was passiert automatisch?**

- Nach einer **Besamung** berechnet die App den **erwarteten Geburtstermin**
  (Rind: 280 Tage, Schaf: 150 Tage, Schwein: 114 Tage, Ziege: 150 Tage)
- Nach einer **Brunft** wird die **nächste Brunft** vorgemerkt
- Im Dashboard erscheint ein **Geburten-Hinweis** wenn es bald so weit ist

---

## 5. Kosten eintragen

**So geht's:**

1. Auf dem Dashboard auf den **Tiernamen** klicken
2. Im Bereich „Kosten“ rechts oben auf **„+ Eintragen“** drücken
3. **Kostenart** auswählen:
   - Tierarzt
   - Besamung
   - Futter
   - Medikamente
   - Impfung
   - Sonstiges
4. **Betrag** eingeben (z.B. `150` oder `150,50`)
5. **Datum** und optionale **Notiz** ergänzen
6. Auf **„Speichern“** drücken

Alle Kosten werden in der **Statistik** und im **PDF-Bericht** zusammengefasst.

---

## 6. Statistik & Auswertung

Oben im Menü auf **„Statistik“** klicken.

Dort siehst du:

| Auswertung | Erklärung |
|---|---|
| **Kosten pro Tier** | Welches Tier hat am meisten gekostet? |
| **Kosten nach Art** | Wofür wurde am meisten ausgegeben? (Tierarzt, Futter …) |
| **Monatsverlauf** | Kosten der letzten 12 Monate im Überblick |
| **Trächtigkeitsrate** | Wie viele Besamungen führten zur Geburt? |

**Hinweis:** Die Auswertungen werden aussagekräftiger, je mehr Daten eingetragen sind.

---

## 7. Export: CSV & PDF

Oben im Menü auf **„Export“** klicken.

### CSV (für Excel)

- Alle Tiere, Ereignisse und Kosten in einer Tabellendatei
- Öffnet sich in Excel, LibreOffice oder Google Tabellen
- Ideal für eigene Auswertungen oder Steuerberater

### PDF-Bericht

- Professionell formatierter Bericht
- Enthält: Tierliste, Kostenübersicht, Ereignisse je Tier
- Ideal zum Ausdrucken oder per E-Mail verschicken

---

## 8. Telegram-Befehle

Mit Telegram kannst du **alles Wichtige direkt vom Handy** aus machen —
auch wenn du nicht im Heimnetz bist.

### Abfragen

| Befehl | Was passiert |
|--------|------------------|
| `/status` | Vollständiger Überblick: Brunft, Trächtigkeit, Geburten |
| `/tiere` | Liste aller aktiven Tiere |
| `/hilfe` | Diese Befehlsliste |

### Eintragen (direkt aus dem Stall)

| Befehl | Beispiel | Erklärung |
|--------|----------|-----------|
| `/besamung` | `/besamung Emma` | Besamung heute für Emma |
| `/besamung` | `/besamung Emma 24.05.` | Besamung mit Datum |
| `/brunft` | `/brunft Bella` | Brunft heute für Bella |
| `/geburt` | `/geburt Lisa` | Geburt heute für Lisa |
| `/impfung` | `/impfung Anna` | Impfung heute für Anna |
| `/tierarzt` | `/tierarzt Emma 150` | Tierarzt 150 € für Emma |
| `/kosten` | `/kosten Emma 80` | Sonstige Kosten 80 € |

**Tipps für Tiernamen:**
- Groß/Kleinschreibung egal: `/besamung emma` funktioniert genauso
- Abkürzung reicht: `/besamung em` findet „Emma“
- Bei mehreren ähnlichen Namen fragt der Bot nach

**Was bekomme ich automatisch?**

Täglich um **6:00 Uhr früh** schickt dir der Bot eine Nachricht,
wenn in den nächsten 14 Tagen eine Geburt erwartet wird.

---

## 9. Häufige Fragen

**Ich habe die App versehentlich geschlossen. Sind meine Daten weg?**
Nein. Alle Daten sind dauerhaft gespeichert. Einfach den Link wieder öffnen.

**Ich habe ein Tier falsch eingetragen. Wie ändere ich das?**
Auf den Tiernamen klicken → „Bearbeiten“ → Änderungen speichern.

**Ich habe ein Ereignis falsch eingetragen. Wie lösche ich es?**
Auf den Tiernamen klicken → Im Bereich „Ereignisse“ beim falschen Eintrag
auf das Papierkorb-Symbol klicken.

**Die App fragt mich beim Öffnen nach einer Farm-Einrichtung.**
Das passiert wenn du einen anderen Browser oder ein anderes Gerät verwendest.
Die Farm-ID steckt im Browser-Speicher. Lösung: Den Link mit der Farm-ID
verwenden (sieht so aus: `https://...railway.app?farm_id=abc123`).
Diesen Link bekommst du von dem, der die App eingerichtet hat.

**Die Geburtsterm-Berechnung stimmt nicht.**
Prüfe ob die richtige **Tierart** beim Tier eingestellt ist
(Rind = 280 Tage, Schaf = 150 Tage, Schwein = 114 Tage).
Tierart ändern: Tier anklicken → Bearbeiten.

**Der Telegram-Bot antwortet nicht.**
Prüfe ob Token und Chat-ID in der App unter
**Menü → Einstellungen → Telegram** eingetragen sind.
Dann einmal `/start` an den Bot schicken.

**Ich möchte alle Daten sichern.**
Oben im Menü auf **Export → CSV** klicken und die Datei speichern.
Das ist deine Datensicherung.

---

*Tierkalb — gemacht für den Betrieb, nicht für den Computer.*
