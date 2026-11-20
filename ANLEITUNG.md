# HerdenPilot — Bedienungsanleitung

**Für den täglichen Gebrauch am Betrieb.** Diese Anleitung findest du auch in der App: Menü → **Anleitung**.

---

## Inhalt

1. [App öffnen](#1-app-öffnen)
2. [Erste Einrichtung](#2-erste-einrichtung)
3. [Das Dashboard: deine Termine](#3-das-dashboard-deine-termine)
4. [Kuh wurde besamt – was jetzt?](#4-kuh-wurde-besamt--was-jetzt)
5. [Tier anlegen](#5-tier-anlegen)
6. [Ereignis eintragen](#6-ereignis-eintragen)
7. [Kosten eintragen](#7-kosten-eintragen)
8. [Telegram: alles vom Stall aus](#8-telegram-alles-vom-stall-aus)
9. [Einstellungen](#9-einstellungen)
10. [Statistik und Export](#10-statistik-und-export)
11. [Updates](#11-updates)
12. [Häufige Fragen](#12-häufige-fragen)

---

## 1. App öffnen

HerdenPilot läuft im Browser, wie eine normale Webseite. Du brauchst **keine Installation** und keinen App-Store.

**Am Handy oder Computer:** den Link öffnen, den du bekommen hast.

**Tipp: App auf den Startbildschirm legen**

- iPhone/iPad: Safari → Teilen-Symbol → „Zum Home-Bildschirm“
- Android: Chrome → Menü (⋮) → „Zum Startbildschirm hinzufügen“

Danach hast du ein Symbol wie bei einer echten App.

Ist ein **Passwort** eingerichtet, fragt die App beim Öffnen danach. Abmelden kannst du oben im Menü.

---

## 2. Erste Einrichtung

Beim allerersten Öffnen erscheint der **Einrichtungs-Assistent**:

1. **Betriebsname** eingeben (z. B. „Hof Huber“)
2. **Deinen Namen** eingeben (optional)
3. **Sprache** wählen
4. **„Betrieb erstellen“** drücken

Die Tierarten Rinder, Schafe, Schweine und Ziegen sind schon angelegt, mit passenden Fristen (siehe [Einstellungen](#9-einstellungen)).

**Danach:** Tiere anlegen und bei jeder Kuh die **letzte Brunft oder Besamung** eintragen. Erst dann kann die App Termine berechnen.

---

## 3. Das Dashboard: deine Termine

Ganz oben auf dem Dashboard steht, **was bei welcher Kuh als Nächstes ansteht**. Sortiert ist nach Dringlichkeit:

| Bereich | Bedeutung |
|---|---|
| ⚠️ **Überfällig** | Hätte schon erledigt sein sollen |
| 📌 **Heute** | Heute dran |
| 📅 **Nächste 7 Tage** | Kommt diese Woche |
| 🗓 **Später** | Weiter in der Zukunft, z. B. Kalbungen |

**Was die Zeichen bedeuten:**

| Zeichen | Termin | Was du tust |
|---|---|---|
| 🔴 | **wieder stierig: nachbesamen!** | Besamer rufen, danach die Besamung eintragen |
| 👀 | **Auf Stierigkeit achten (Tag 21)** | Kuh beobachten. Stierig? → Brunft eintragen |
| 🔬 | **Trächtigkeitsuntersuchung (Tag 28)** | Untersuchen lassen, danach das Ergebnis eintragen |
| ⚠️ | **Ergebnis Trächtigkeitsuntersuchung eintragen** | Die Untersuchung ist vorbei, das Ergebnis fehlt noch |
| 🐣 | **Kalbung erwartet** | Kalbetermin. „nicht bestätigt“ heißt: ohne Untersuchung |
| ⚠️ | **Kalbung überfällig?** | Termin vorbei. Geburt eintragen, falls schon gekalbt |
| 🌸 | **Brunft erwartet** | Auf Stierigkeit achten (Kuh ist nicht trächtig) |

Ein Tipp auf einen Termin öffnet die Kuh.

Darunter siehst du die Zahlen (Tiere, Kosten, Kalbungen in 30 Tagen) und die Liste der Tiere. Sie ist in **Reiter** aufgeteilt:

**Alle · 🐄 Kühe · 🐮 Färsen · 🍼 Kälber · 🐂 Stiere**, jeweils mit Anzahl. Die App merkt sich, welchen Reiter du zuletzt offen hattest.

---

## 4. Kuh wurde besamt – was jetzt?

Das ist der wichtigste Ablauf. HerdenPilot führt dich Schritt für Schritt durch:

**① Besamung eintragen**

Am Tier → Ereignis → 💉 **Besamung**, oder per Telegram `/besamung Emma`.
Die App plant sofort die nächsten Termine ein.

**② Tag 21: auf Stierigkeit achten** 👀

Die Kuh erscheint im Dashboard unter „Auf Stierigkeit achten“.

- **Wieder stierig?** → 🌸 **Brunft** eintragen. Die App meldet 🔴 **„nachbesamen!“**
  → nachbesamen lassen → **neue Besamung** eintragen. Der Ablauf beginnt von vorn.
- **Nicht stierig?** → nichts tun, weiter zu ③.

**③ Tag 28: Trächtigkeitsuntersuchung** 🔬

Nach der Untersuchung das Ergebnis eintragen:

- ✅ **TU: trächtig**, per Telegram `/tk Emma ja`
  → Die App zeigt den **Kalbetermin** (Rind: 290 Tage nach der Besamung).
- ❌ **TU: nicht trächtig**, per Telegram `/tk Emma nein`
  → Die App erwartet die nächste Brunft. Wieder stierig? → Brunft eintragen → nachbesamen.

**④ Kalbung** 🐣

Wenn die Kuh gekalbt hat: 🐣 **Geburt** eintragen. Danach ist sie wieder „offen“, und der Kreislauf beginnt mit der nächsten Brunft.

> Brunft und Besamung am **selben Tag** einzutragen ist richtig. Das löst kein „nachbesamen“ aus, erst eine Brunft ein paar Tage später.

> **Ältere Besamungen nachtragen?** Kein Problem. Ist die Besamung länger als 60 Tage her und kein Ergebnis eingetragen, gilt die Kuh als „vermutlich trächtig“ und bekommt einen Kalbetermin. Mit dem Untersuchungsergebnis wird daraus ein bestätigter Termin.

---

## 5. Tier anlegen

1. Auf dem Dashboard oben rechts **„+ Neues Tier“** drücken
2. Felder ausfüllen:

| Feld | Erklärung | Pflicht? |
|------|-----------|----------|
| **Name** | z. B. „Emma“ | Ja |
| **Ohrmarke** | Amtliche Nummer, z. B. DE 09 123 45678 | Empfohlen |
| **Tierart** | Rind, Schaf, Schwein, Ziege | **Ja, für die Termine** |
| **Geschlecht** | Weiblich / Männlich | Nein |
| **Kategorie** | Kuh, Färse, Kalb oder Stier: bestimmt den Reiter im Dashboard | Ja (vorausgewählt) |
| **Geburtsdatum** | Geburtstag des Tieres | Nein |
| **Notiz** | Interne Anmerkung | Nein |

3. **„Speichern“** drücken

> ⚠️ **Ohne Tierart gibt es keine Termine.** Die Fristen hängen an der Tierart.
> 🐮 **Färse = noch nicht gekalbt.** Sobald du bei einer Färse eine **Geburt** einträgst, wird sie **automatisch zur Kuh**. Kälber und Stiere wechselst du bei Bedarf von Hand (Bearbeiten → Kategorie).

> 💡 **Ohrmarke eintragen lohnt sich.** Über sie lassen sich später Daten zuordnen, etwa bei einem Import.

**Bearbeiten:** Tier antippen → „Bearbeiten“
**Archivieren** (verkauft, abgegangen): Tier antippen → „Archivieren“. Die Daten bleiben erhalten.

Schneller per Telegram: `/neues_tier Emma Kuh`, `/neues_tier Resi Färse`, `/neues_tier Bambi Kalb` oder `/neues_tier Max Stier`

---

## 6. Ereignis eintragen

1. Auf dem Dashboard das **Tier** antippen
2. Bei „Ereignisse“ auf **„+ Eintragen“**
3. **Art** wählen:
    - 🌸 **Brunft**: Tier ist stierig
    - 💉 **Besamung**: Tier wurde besamt
    - ✅ **TU: trächtig** / ❌ **TU: nicht trächtig**: Ergebnis der Trächtigkeitsuntersuchung
    - 🐣 **Geburt**: Tier hat gekalbt
    - 🩺 **Tierarzt / Impfung**: Tierarztbesuch oder Impfung, die Art in die Notiz schreiben
    - 📝 **Sonstiges**: beliebiger Vermerk
4. **Datum** prüfen (Standard: heute). Ältere Ereignisse einfach mit dem richtigen Datum eintragen.
5. Bei Besamung, Untersuchung und Tierarzt kannst du gleich die **Kosten** mit angeben.
6. **„Speichern“**

Auf der Seite des Tiers steht oben der **aktuelle Stand** (z. B. „besamt 03.11. (Tag 17)“) mit den nächsten Terminen.

**Falsch eingetragen?** Beim Eintrag auf den Papierkorb tippen und neu eintragen.

---

## 7. Kosten eintragen

1. **Tier** antippen → bei „Kosten“ auf **„+ Eintragen“**
2. **Kostenart:** Tierarzt (auch Impfung) / Besamung / Futter / Medikamente / Sonstiges
3. **Betrag** (z. B. `150` oder `150,50`), Datum, Notiz
4. **„Speichern“**

Per Telegram: `/tierarzt Emma 150` oder `/kosten Emma 80`

---

## 8. Telegram: alles vom Stall aus

Mit Telegram trägst du direkt vom Handy ein, ohne die App zu öffnen. Jeden Morgen kommt eine **Übersicht der Termine**. Einrichten: siehe [Einstellungen](#9-einstellungen).

### Abfragen

| Befehl | Was passiert |
|--------|---------------|
| `/status` | Alle Termine und eine Übersicht der Herde |
| `/tiere` | Liste aller Tiere, nach Kühen, Färsen, Kälbern und Stieren |
| `/hilfe` | Alle Befehle |

### Eintragen

| Befehl | Beispiel | Bedeutung |
|--------|----------|-----------|
| `/besamung` | `/besamung Emma` | Besamung heute |
| | `/besamung Emma 03.11.` | Besamung an einem früheren Tag |
| | `/besamung Emma 85` | Besamung mit 85 € Kosten |
| `/brunft` | `/brunft Emma` | Kuh ist stierig. Nach einer Besamung meldet die App „nachbesamen!“ |
| `/tk` | `/tk Emma ja` | Untersuchung: trächtig |
| | `/tk Emma nein` | Untersuchung: nicht trächtig |
| `/geburt` | `/geburt Emma` | Kuh hat gekalbt |
| `/impfung` | `/impfung Emma` | Impfung (wird als Tierarzt eingetragen) |
| `/tierarzt` | `/tierarzt Emma 150` | Tierarztkosten 150 € |
| `/kosten` | `/kosten Emma 80` | Sonstige Kosten 80 € |
| `/neues_tier` | `/neues_tier Resi Färse` | Neues Tier anlegen (Kuh, Färse, Kalb oder Stier) |

**Tipps:**

- Groß- und Kleinschreibung ist egal, eine Abkürzung reicht: `/besamung em` findet „Emma“
- Ein Datum hängst du hinten an, z. B. `/brunft Emma 18.11.`

---

## 9. Einstellungen

Oben im Menü → **Einstellungen**. Danach unten **„Speichern“** drücken.

**Tierarten & Fristen**

Hier stehen die Tage, mit denen die Termine berechnet werden. Für Rinder (Fleckvieh) ist voreingestellt:

| Frist | Wert | Wofür |
|---|---|---|
| Brunftzyklus | 21 Tage | Wann nach der Besamung auf Stierigkeit achten |
| Untersuchungstag | 28 Tage | Wann die Trächtigkeitsuntersuchung ansteht |
| Tragzeit | 290 Tage | Wann die Kalbung erwartet wird |

Passt ein Wert bei dir nicht, kannst du ihn hier ändern. Alle Termine richten sich sofort danach.

**Zugriffsschutz**

Passwort eintragen = beim Öffnen wird danach gefragt. Leer lassen = kein Passwort.

**Benachrichtigungen**

- **Uhrzeit** der täglichen Übersicht (Standard 6:00)
- **Kanäle** einschalten, auch mehrere zugleich:
    - **Telegram**: Übersicht und Eingabe vom Stall aus (empfohlen)
    - **ntfy**: einfache Push-Nachricht aufs Handy, ohne Konto
    - **E-Mail**
- Bei jedem Kanal steht eine **Einrichtungsanleitung zum Aufklappen**, dazu der Knopf **„Testmeldung senden“**.

**Telegram kurz:** In Telegram bei **@BotFather** mit `/newbot` einen Bot anlegen und den Token kopieren. Bei **@userinfobot** die Chat-ID holen. Beides eintragen und speichern. Dann den eigenen Bot öffnen und **einmal „Start“ drücken**, sonst darf er dir nicht schreiben. Zum Schluss die Testmeldung senden.

---

## 10. Statistik und Export

**Statistik** (Menü): Kosten pro Tier und nach Art, Monatsverlauf, Besamungserfolg, Kosten pro Geburt.

**Export** (Menü):

- **CSV**: alle Tiere, Ereignisse und Kosten als Tabelle für Excel. Taugt auch als **Datensicherung**.
- **PDF**: fertiger Bericht zum Ausdrucken oder Verschicken.

---

## 11. Updates

Menü → Einstellungen → ganz unten **„Auf Updates prüfen“**.

- ✅ **„neuester Stand“**: nichts zu tun
- 🔵 **„neue Änderungen verfügbar“**: Die Liste zeigt, was neu ist
    - **Raspberry Pi / Server:** **„Jetzt aktualisieren“** drücken oder in Telegram `/update` senden. Nach 2–5 Minuten kommt „✅ Update abgeschlossen“. Die App ist in dieser Zeit kurz nicht erreichbar.
    - **Windows:** HerdenPilot schließen und `update.bat` doppelklicken. Die genaue Anleitung steht auf der Update-Seite.

**Deine Daten bleiben bei jedem Update erhalten.**

---

## 12. Häufige Fragen

**Sind meine Daten weg, wenn ich die App schließe?**

Nein. Alles ist dauerhaft gespeichert. Einfach den Link wieder öffnen.

**Bei einer Kuh stehen keine Termine.**

Prüfe, ob eine **Tierart** eingestellt ist (Tier → Bearbeiten) und ob die letzte **Brunft oder Besamung** eingetragen ist. Ohne diese Angaben kann die App nichts berechnen. Steht das Tier unter **Kälber**, gibt es bewusst keine Besamungs-Termine. Dann die Kategorie auf **Färse** stellen.

**Ich habe das falsche Untersuchungsergebnis eingetragen.**

Tier antippen → beim Eintrag auf den Papierkorb → richtiges Ergebnis neu eintragen.

**Die Kuh wurde nachbesamt, aber im Dashboard steht noch „nachbesamen!“.**

Die neue **Besamung** eintragen. Dann verschwindet der Hinweis, und die neuen Termine erscheinen.

**Der Kalbetermin passt nicht.**

Prüfe das Datum der Besamung. Grundsätzlich falsch? Die **Tragzeit** unter Einstellungen → Tierarten & Fristen anpassen.

**Der Telegram-Bot antwortet nicht.**

Token und Chat-ID unter Einstellungen prüfen. Beim eigenen Bot einmal „Start“ gedrückt? Dann „Testmeldung senden“. Neue Einstellungen übernimmt der Bot innerhalb von etwa 5 Minuten.

**Eine Kuh steht bei den Färsen (oder umgekehrt).**

Tier antippen → „Bearbeiten“ → **Kategorie** ändern. Beim Update wurden alle schon eingetragenen weiblichen Rinder als Kuh eingeordnet. Deine Färsen stellst du deshalb einmal um.

**Ich möchte eine Datensicherung.**

Menü → Export → **CSV** und die Datei speichern.

---

*HerdenPilot — gemacht für den Betrieb, nicht für den Computer.*
