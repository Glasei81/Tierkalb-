# Tierkalb — Bedienungsanleitung

**Für den täglichen Gebrauch am Betrieb**

---

## Inhalt

1. [App öffnen](#1-app-öffnen)
2. [Erste Einrichtung](#2-erste-einrichtung)
3. [Tier anlegen](#3-tier-anlegen)
4. [Ereignis eintragen](#4-ereignis-eintragen)
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
Den Link im Browser öffnen (du hast ihn per WhatsApp o. ä. bekommen).

**Tipp — App auf dem Handy-Startbildschirm installieren:**
- iPhone: Safari → Teilen-Symbol → „Zum Home-Bildschirm“
- Android: Chrome → Menü (⋮) → „Zum Startbildschirm hinzufügen“

Danach hast du ein Symbol wie eine echte App und kannst sie wie gewöhnt tippen.

---

## 2. Erste Einrichtung

Beim allerersten Öffnen erscheint der **Einrichtungs-Assistent**.

1. **Betriebsname** eingeben (z. B. „Hof Mustermann“)
2. **Deinen Namen** eingeben (optional)
3. **Sprache** wählen: Deutsch oder Englisch
4. Auf **„Betrieb erstellen“** drücken

Die Tierarten sind bereits voreingestellt: Rinder, Schafe, Schweine, Ziegen und Hühner.

**Fertig** — du bist auf dem Dashboard.

---

## 3. Tier anlegen

**So geht's:**

1. Auf dem Dashboard oben rechts auf **„+ Neues Tier“** drücken
2. Felder ausfüllen:

| Feld | Erklärung | Pflicht? |
|------|-----------|----------|
| **Name** | Freiname, z. B. „Emma“ | Ja |
| **Ohrmarke** | Amtliche Nummer, z. B. AT 123456789 | Nein |
| **Tierart** | Rind, Schaf, Schwein, Ziege, Huhn | Empfohlen |
| **Geschlecht** | Weiblich / Männlich | Nein |
| **Geburtsdatum** | Eigenes Geburtsdatum des Tieres | Nein |
| **Notiz** | Interne Anmerkung | Nein |

3. Auf **„Speichern“** drücken

> ⚠️ **Tierart nicht vergessen!** Ohne Tierart wird kein Geburtstermin berechnet.
> Die App warnt dich, wenn du das Feld leer lässt.

Das Tier erscheint jetzt auf dem Dashboard.

**Tier bearbeiten:** Auf den Namen klicken → „Bearbeiten“  
**Tier archivieren:** Auf den Namen klicken → „Archivieren“ (Daten bleiben erhalten)

---

## 4. Ereignis eintragen

Ereignisse sind alles was mit dem Tier passiert: Brunft, Besamung, Geburt, Impfung, Tierarzt, Sonstiges.

**So geht's:**

1. Auf dem Dashboard auf den **Tiernamen** klicken
2. Im Bereich „Ereignisse“ auf **„+ Eintragen“** drücken
3. **Ereignis-Typ** auswählen:
   - 🌸 **Brunft** — Tier ist stierig
   - 💉 **Besamung** — Tier wurde besamt
   - 🐣 **Geburt** — Tier hat gekalbt / gelammt / geferkelt
   - 💊 **Impfung** — Impfung durchgeführt
   - 🩺 **Tierarzt** — Tierarztbesuch
   - 📝 **Sonstiges** — Beliebiger Vermerk
4. **Datum** eintragen (Standard: heute)
5. **Notiz** hinzufügen (optional)
6. Auf **„Speichern“** drücken

**Was passiert automatisch?**

- Nach einer **Besamung** berechnet die App den **erwarteten Geburtstermin**:

| Tierart | Tragzeit |
|---------|----------|
| 🐄 Rinder | 280 Tage |
| 🐑 Schafe | 150 Tage |
| 🐷 Schweine | 114 Tage |
| 🐐 Ziegen | 150 Tage |
| 🐔 Hühner | 21 Tage (Brutzeit) |

- Nach einer **Brunft** wird die nächste Brunft vorgemerkt
- Im Dashboard erscheint ein **Geburten-Hinweis** wenn es bald so weit ist

---

## 5. Kosten eintragen

**So geht's:**

1. Auf dem Dashboard auf den **Tiernamen** klicken
2. Im Bereich „Kosten“ auf **„+ Eintragen“** drücken
3. **Kostenart** auswählen: Tierarzt / Besamung / Futter / Medikamente / Impfung / Sonstiges
4. **Betrag** eingeben (z. B. `150` oder `150,50`)
5. **Datum** und optionale **Notiz** ergänzen
6. Auf **„Speichern“** drücken

Alle Kosten werden in der **Statistik** und im **PDF-Bericht** zusammengefasst.

---

## 6. Statistik & Auswertung

Oben im Menü auf **„Statistik“** klicken.

| Auswertung | Erklärung |
|---|---|
| **Kosten pro Tier** | Welches Tier hat am meisten gekostet? |
| **Kosten nach Art** | Wofür wurde am meisten ausgegeben? |
| **Monatsverlauf** | Kosten der letzten 12 Monate |
| **Trächtigkeitsrate** | Wie viele Besamungen führten zur Geburt? |

---

## 7. Export: CSV & PDF

Oben im Menü auf **„Export“** klicken.

**CSV (für Excel):** Alle Tiere, Ereignisse und Kosten als Tabelle — öffnet sich in Excel, LibreOffice oder Google Tabellen.

**PDF-Bericht:** Professionell formatierter Bericht mit Tierliste, Kostenübersicht und Ereignissen — ideal zum Ausdrucken oder per E-Mail.

---

## 8. Telegram-Befehle

Mit Telegram kannst du alles Wichtige direkt vom Handy aus machen — auch wenn du nicht im Heimnetz bist.

### Abfragen

| Befehl | Was passiert |
|--------|--------------|
| `/status` | Vollständiger Überblick: Brunft, Trächtigkeit, Geburten |
| `/tiere` | Liste aller aktiven Tiere |
| `/hilfe` | Diese Befehlsliste |

### Tiere anlegen

| Befehl | Beispiel | Erklärung |
|--------|----------|-----------|
| `/neues_tier` | `/neues_tier Emma Rind` | Kuh „Emma“ anlegen |
| `/neues_tier` | `/neues_tier Wolke Schaf` | Schaf „Wolke“ anlegen |

Verfügbare Tierarten: Rind, Schaf, Schwein, Ziege, Huhn  
Ohrmarke und Geburtsdatum kannst du danach in der App ergänzen.

### Eintragen (direkt aus dem Stall)

| Befehl | Beispiel | Erklärung |
|--------|----------|-----------|
| `/besamung` | `/besamung Emma` | Besamung heute |
| `/besamung` | `/besamung Emma 24.05.` | Besamung mit Datum |
| `/brunft` | `/brunft Bella` | Brunft heute |
| `/brunft` | `/brunft Bella 20.05.` | Brunft mit Datum |
| `/geburt` | `/geburt Lisa` | Geburt heute |
| `/geburt` | `/geburt Lisa 18.05.` | Geburt mit Datum |
| `/impfung` | `/impfung Anna` | Impfung heute |
| `/tierarzt` | `/tierarzt Emma 150` | Tierarzt 150 € |
| `/kosten` | `/kosten Emma 80` | Sonstige Kosten 80 € |

**Tipps:**
- Groß/Kleinschreibung egal: `/besamung emma` funktioniert genauso wie `/besamung Emma`
- Abkürzung reicht: `/besamung em` findet „Emma“
- Bei mehreren ähnlichen Namen fragt der Bot nach

Täglich um **6:00 Uhr früh** kommt automatisch eine Nachricht wenn Geburten bevorstehen.

---

## 9. Häufige Fragen

**Ich habe die App versehentlich geschlossen. Sind meine Daten weg?**  
Nein. Alle Daten sind dauerhaft gespeichert. Einfach den Link wieder öffnen.

**Ich habe ein Tier falsch eingetragen. Wie ändere ich das?**  
Auf den Tiernamen klicken → „Bearbeiten“ → Änderungen speichern.

**Ich habe ein Ereignis falsch eingetragen. Wie lösche ich es?**  
Auf den Tiernamen klicken → im Bereich „Ereignisse“ beim falschen Eintrag auf das Papierkorb-Symbol.

**Die App öffnet das Setup obwohl ich schon eingerichtet habe.**  
Das passiert beim ersten Öffnen auf einem neuen Gerät oder Browser. Einfach den Link öffnen, den dir der Betreiber geschickt hat — nach dem ersten Besuch merkt sich der Browser den Betrieb dauerhaft.

**Die Geburtstermin-Berechnung stimmt nicht.**  
Prüfe ob die richtige **Tierart** beim Tier eingestellt ist (Tier anklicken → Bearbeiten). Ohne Tierart gibt es keinen Geburtstermin.

**Der Telegram-Bot antwortet nicht.**  
Token und Chat-ID in der App unter **Menü → Einstellungen** prüfen. Den „Testnachricht senden“-Button verwenden — der zeigt sofort ob die Verbindung klappt.

**Ich möchte alle Daten sichern.**  
Oben im Menü auf **Export → CSV** klicken und die Datei speichern.

---

*Tierkalb — gemacht für den Betrieb, nicht für den Computer.*
