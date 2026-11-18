# HerdenPilot — Roadmap & Entwicklungsprotokoll

> Lebendes Dokument. Es hält fest, **was** gebaut wurde, **warum** — und **wie man einen Schritt zurückgeht**.
> Bei jeder größeren Änderung hier nachtragen (siehe [Pflege](#9-pflege-dieses-dokuments)).

**Inhalt**
1. [Aktueller Stand](#1-aktueller-stand)
2. [Entwicklungsverlauf](#2-entwicklungsverlauf)
3. [Entscheidungen — mit Begründung und Rückweg](#3-entscheidungen)
4. [Fehler & Lehren](#4-fehler--lehren)
5. [Offene Punkte](#5-offene-punkte)
6. [Ideen-Speicher](#6-ideen-speicher)
7. [Gesprächsleitfaden Vinzenz](#7-gesprächsleitfaden-vinzenz)
8. [Einen Schritt zurück — so geht's](#8-einen-schritt-zurück--so-gehts)
9. [Pflege dieses Dokuments](#9-pflege-dieses-dokuments)

---

## 1. Aktueller Stand

*Stand: 18.11.2026*

**Was HerdenPilot kann**
- Tiere verwalten; Brunft, Besamung, Trächtigkeitskontrolle, Geburt, Impfung, Tierarzt, Kosten
- Dashboard mit Warnungen (Geburt bald, Brunft in 7 Tagen, TK fällig, Impfung fällig)
- Statistik (Kosten, Besamungserfolg, Kosten pro Geburt), Export als CSV und PDF
- Tägliche Meldung über **Telegram, ntfy.sh und/oder E-Mail** — Uhrzeit je Betrieb einstellbar
- Telegram zusätzlich zur Eingabe aus dem Stall (`/besamung Emma`, `/status` …)
- Optionaler Passwortschutz, Update-Prüfung, Update per `/update` bzw. Knopf

**Betriebsarten**

| Betriebsart | Für wen | Update |
|---|---|---|
| Windows-exe (auch vom USB-Stick) | Einsteiger, ohne Server | Prüfung gegen Release → `update.bat` |
| Raspberry Pi / Docker | Dauerbetrieb, Morgenmeldung 24/7 | Prüfung gegen Code-Stand → `/update` oder Knopf |
| Zugriff per Tailscale | von unterwegs, iPad/Handy | — |

**Laufende Installationen**
- **hauspi (Stefan):** Docker, Tailscale Funnel aktiv. Derzeit **Testbetrieb Vinzenz** im Ordner `data`; Stefans Demo geparkt in `data_demo`. Bewusst ohne Passwort (Testphase) → siehe [Offene Punkte](#5-offene-punkte).

---

## 2. Entwicklungsverlauf

| Datum | Schritt | Inhalt |
|---|---|---|
| 25.03.2026 | **v2.0** „Tierkalb" | Web-App mit Einrichtungs-Assistent, Flask, Telegram |
| 27.05.–01.06. | **v3.0** | Überarbeitung; Telegram `/status` und Eingabe aus dem Stall; Bedienungsanleitung; Spendenseite; Update-Skripte; Datenbank bleibt bei Updates erhalten (Bind-Mount) |
| 01.–02.06. | **v3.1** | Schlüssel-Fix, gemerkter Betrieb, PWA, Besamungskosten, Erinnerung Trächtigkeitskontrolle, einzelner Betrieb lädt automatisch |
| 03.06. | **v3.2** | Kosten direkt beim Ereignis, Statistik nach Tierart, männliche Tiere aus Brunft-Logik ausgenommen |
| 04.06. | **v3.3** | Hühner entfernt, Besamungs-Statistik, Impf-Erinnerung, Brunft-Warnung 7 Tage; Zeitzonen-Fix |
| 10.–11.06. | **Umbenennung → HerdenPilot** | Neuer Name; Windows-exe per GitHub Actions; Impf-Erinnerung entschärft; Installationsanleitung neu |
| 22.–24.06. | Online & Kanäle | Passwort-Login; Fly.io vorbereitet (später verworfen, E04); **Multi-Kanal-Benachrichtigungen** |
| 28.07. | Updates I | Update-Prüfung (Browser, `/version`), `update.bat` für die exe |
| 18.11. | Updates II & Feinschliff | Passwort aus `.env`; **Meldezeit einstellbar**; **Passwort in den Einstellungen**; **`/update` per Telegram/Knopf** + Pi-Setup-Skript; Cookie-Fix; Update-Prüfung gegen Code-Stand; `.dockerignore`; Formular-Fix Einstellungen; diese Roadmap |

Details zu jedem Schritt: `git log` bzw. die Commit-Liste auf GitHub.

---

## 3. Entscheidungen

Jede Weichenstellung mit **Warum**, **Verworfenes** und **Rückweg**. Verworfene Entscheidungen bleiben stehen — mit Status.

### E01 — Name „HerdenPilot" · *10.06.2026 · gilt*
- **Warum:** „Tierkalb" zu eng und wenig griffig. Positionierung: *professionelles Herdenmanagement ohne teure Lizenzen.*
- **Rückweg:** reine Text-/Oberflächenänderung (Commits `556bd5e`, `f4c17d3`, `8d2e36d`, `a1f89f4`).

### E02 — Brunft und Zucht vor Gesundheit · *11.06.2026 · gilt*
- **Warum:** Kernzweck ist das Brunft-Tracking. Die Impf-Erinnerung listete jedes nie geimpfte Tier und überdeckte das Wichtige.
- **Entscheidung:** Impf-Erinnerung nur für Tiere mit mindestens einer eingetragenen Impfung.
- **Rückweg:** `database.get_faellige_impfungen` — `JOIN` wieder zu `LEFT JOIN` (Commit `c02f1fb`).

### E03 — Hühner entfernt · *04.06.2026 · gilt*
- **Warum:** passen nicht in die Brunft-/Trächtigkeitslogik, um die sich die App dreht.
- **Rückweg:** Eintrag in `tierarten.py` (Commit `c29333c`).

### E04 — Lokal statt Cloud · *22.06. vorbereitet → 18.11.2026 verworfen*
- **Ausgangslage:** Ein Kollege kam mit dem iPad → Fly.io-Hosting vorbereitet (`fly.toml`, DEPLOYMENT „Variante 4").
- **Verworfen, weil:** wenig Bedarf; Betriebsdaten sollen auf dem Hof bleiben. Fernzugriff stattdessen über **Tailscale** (privat) bzw. **Tailscale Funnel** (öffentlicher Link).
- **Rückweg:** `fly.toml` liegt noch im Repo, Anleitung in DEPLOYMENT.md Variante 4.

### E05 — SQLite bleibt; serverloses Muster (Vercel/Postgres) geprüft, nicht übernommen · *18.11.2026 · gilt*
- **Warum:** Die Morgenmeldung und der Telegram-Empfang sind Dauerprozesse — die passen nicht zu serverlosem Hosting. Bei einem Betrieb und wenigen Nutzern bringt Postgres keinen Vorteil.
- **Option für später:** Der gesamte Datenbankzugriff steckt in `database.py` → ein Wechsel wäre eine Ein-Datei-Änderung (Platzhalter `?`→`%s`, Datumsfunktionen).

### E06 — Drei gleichberechtigte Betriebsarten („Systemoffenheit") · *11.06.2026 · gilt*
- **Warum:** Niemand soll zu einem Weg gezwungen werden. exe für Einsteiger, Docker/Pi für Dauerbetrieb, Tailscale für Zugriff. Mac: über Docker.
- **USB-Stick:** Die exe legt ihre Daten neben sich ab → Stick mit exe (+ optional vorbereitetem `data`-Ordner) ist eine mobile Installation.

### E07 — Mehrere Benachrichtigungskanäle · *24.06.2026 · gilt*
- **Warum:** Nicht jeder nutzt Telegram. ntfy.sh braucht kein Konto, E-Mail hat jeder. Alle aktiven Kanäle bekommen dieselbe Meldung.
- **Hinweis:** Nur Telegram kann auch Eingaben aus dem Stall entgegennehmen.

### E08 — Zeit: Europe/Berlin, Meldezeit je Betrieb · *04.06. / 18.11.2026 · gilt*
- **Warum:** Standardzeit des Schedulers war UTC (Meldung kam um 8 statt 6 Uhr). Jetzt fest Europe/Berlin; der Scheduler prüft minütlich, ob die eingestellte Uhrzeit eines Betriebs erreicht ist.

### E09 — Passwortschutz zweistufig · *18.11.2026 · gilt*
- **Entscheidung:** Passwort im Feld *Einstellungen → Zugriffsschutz* (gehasht gespeichert) **oder** in der `.env` auf dem Server. Die `.env` hat Vorrang.
- **Warum:** Das Feld ist bequem; die `.env` ist für **öffentlichen** Zugang (Funnel) robuster, weil sie aus der App heraus nicht geändert werden kann.

### E10 — Updates je Betriebsart · *28.07. / 18.11.2026 · gilt*
- **exe:** Vergleich mit dem veröffentlichten Release → `update.bat` tauscht die Datei (die laufende exe kann sich nicht selbst überschreiben).
- **Pi/Docker:** Vergleich des laufenden Code-Stands mit GitHub `main` → `/update` oder Knopf legt eine Anforderung ab, ein **systemd-Dienst auf dem Pi** baut neu (der Container kann sich nicht selbst neu bauen).
- **Bewusst nicht:** unbeaufsichtigtes Auto-Update — ein fehlerhaftes Update könnte den Betrieb unbemerkt lahmlegen.
- **Sicherheitsnetz:** Schlägt der Neubau fehl, läuft die bisherige Version weiter; Telegram meldet den Fehler.

### E11 — Ein Betrieb pro Datenbank · *18.11.2026 · gilt*
- **Warum:** einfach und robust; die App wählt den einzigen Betrieb automatisch.
- **Konsequenz:** Wechsel zwischen Betrieben durch Umbenennen des `data`-Ordners. Mehrere Nutzer in Telegram über eine **Gruppe**. Echte Mandantenfähigkeit wäre ein größerer Umbau.

### E12 — Hardware für Dauerbetrieb · *18.11.2026 · Empfehlung*
- Pi statt exe nur, wenn die Morgenmeldung **24/7** gewünscht ist (PC ist nachts aus).
- Raspberry Pi 4/5 (4 GB), **offizielles Netzteil**, **SSD-Boot** statt SD-Karte, Kühlgehäuse, LAN-Kabel; optional kleine USV.

### E13 — Erst Bedarf klären, dann bauen · *18.11.2026 · gilt*
- **Warum:** Zucht-Ausbau und Import sonst an Vinzenz' tatsächlichem Bedarf vorbei → viele halbe Versionen.
- **Nächster Schritt:** Gespräch nach [Leitfaden](#7-gesprächsleitfaden-vinzenz).

---

## 4. Fehler & Lehren

| Datum | Fehler | Ursache | Lösung | Lehre |
|---|---|---|---|---|
| 04.06. | Morgenmeldung 8:00 statt 6:00 | Scheduler lief in UTC | Zeitzone Europe/Berlin (`1de9975`) | Zeitzonen immer ausdrücklich setzen |
| 11.06. | Impf-Erinnerung listet ganze Herde | „nie geimpft" galt als fällig | nur bereits geimpfte Tiere (`c02f1fb`) | Nebenwarnungen dürfen den Hauptzweck nicht überdecken |
| 18.11. | Einrichtungsseite, obwohl ein Betrieb da ist | Browser merkte sich die ID des alten Betriebs (nach `data`-Tausch) | gemerkte IDs werden geprüft (`34901b2`) | Datenordner-Tausch als Testfall mitdenken |
| 18.11. | Update-Seite „aktuell", obwohl neuer Code da war | Vergleich mit Release statt Code-Stand | Pi vergleicht mit `main` (`86b044f`) | Prüfung muss zur Update-Quelle passen |
| 18.11. | `.env` (Passwort) und `data` landeten im Docker-Image | keine `.dockerignore` | `.dockerignore` (`86b044f`) | — |
| 18.11. | „Speichern" wirkungslos, sobald Telegram eingerichtet war | Testmeldung-Knöpfe als Formular im Formular | Knöpfe mit `formaction` (`4714d28`) | **im echten Browser klicken**, nicht nur Code lesen |

---

## 5. Offene Punkte

**Als Nächstes**
- [ ] **Gespräch mit Vinzenz** nach [Leitfaden](#7-gesprächsleitfaden-vinzenz) — Ergebnis hier eintragen
- [ ] hauspi aktualisieren: `cd ~/Tierkalb- && git pull && sudo bash autoupdate/install-updater.sh`

**Sicherheit / Aufräumen**
- [ ] **hauspi ist per Funnel ohne Passwort öffentlich erreichbar.** Nach der Testphase: Passwort setzen (E09) oder `tailscale funnel off`
- [ ] Erstes GitHub-Release `v1.0` veröffentlichen (für exe-Download und Release-Prüfung)
- [ ] `templates/pro.html` entfernen — altes „Pro/Lizenz"-Template, ohne Route, widerspricht der Positionierung
- [ ] Fly.io aus Repo und Anleitung entfernen? (E04)

**Aufgenommen, wartet auf das Gespräch**
- [ ] **Import-Funktion** — allgemein für Excel/CSV, mit Spaltenzuordnung (siehe Ideen)
- [ ] Recherche Datenquellen Deutschland/Bayern
- [ ] Zucht-Ausbau, Statistik-Ausbau, Layout

---

## 6. Ideen-Speicher

Gesammelte Ideen mit Einschätzung. Umsetzung erst nach Bedarfsklärung (E13).

### Import
- **Allgemeiner Import** (Excel/CSV) mit Spaltenzuordnung — einmal „Spalte C = Ohrmarke" festlegen, wird gemerkt. Zuordnung der Tiere über die **Ohrmarke**.
- **Bestandsliste** importieren statt Tiere einzeln anzulegen — Quelle voraussichtlich **HI-Tier** (zu prüfen).
- **Abstammung / Zuchtwerte** vom Zuchtverband — füllt den Stammbaum sofort mehrere Generationen tief.
- **Ordner-Überwachung:** schreibt ein Programm regelmäßig eine Datei, holt HerdenPilot sie selbst ab.
- **Recherche (Deutschland/Bayern):** HI-Tier, LKV Bayern (Milchleistungsprüfung), RDV, regionaler Zuchtverband, Melkroboter-Hersteller (Lely, DeLaval, GEA …) — welche Exporte/Schnittstellen es gibt, in welchem Format, automatisch oder nur von Hand. Schnittstellen sind erfahrungsgemäß oft nur Vertragspartnern offen; Exportdateien sind der realistische Weg.

### Zucht
**A — Erfassung (klein, je früher desto wertvoller)**
- Besamung: Stier (Name, Nummer, Rasse), gesextes Sperma, Besamer oder Natursprung
- Trächtigkeitskontrolle als eigenes Ergebnis „trächtig ja/nein" (statt Umweg über `/brunft`)
- Geburt: Kalb direkt anlegen — Geschlecht, Gewicht, Kalbeverlauf, lebend/tot, Zwilling
- **Automatik:** Kalb bekommt Mutter (die Kuh) und Vater (Stier der letzten Besamung) selbst zugeordnet
- Tier: Mutter, Vater, Rasse; beim Archivieren ein Abgangsgrund
- Stierliste mit Vorschlägen, auch per Telegram

**B — Statistik, aussagekräftig schon unter einem Jahr**
- Erstbesamungserfolg, Besamungsindex — pro Kuh, Stier, Monat
- Rastzeit, Güstzeit
- Tatsächlicher Brunftzyklus je Kuh (Abweichung = Hinweis für den Tierarzt)
- Kalbeverlauf je Stier, Geschlechterverhältnis, Kalbe-Kalender
- Kosten pro Trächtigkeit
- Jede Kennzahl mit Datenbasis („aus 7 Besamungen"), wählbarem Zeitraum und ehrlichem „noch zu wenig Daten"

**C — wächst über die Jahre**
- Stammbaum je Tier; Töchter-Auswertung je Stier; Kuhfamilien
- Zwischenkalbezeit, Erstkalbealter, Nutzungsdauer

### Milch (sobald ein Melkstand da ist)
- Import der Melkdaten, Verlauf je Kuh, Herdenschnitt
- **Warnung bei Milchrückgang** in der Morgenmeldung (früher Hinweis auf Erkrankung)

### Layout
- Hauptfarbe wählbar, Hoffoto als Kopfbild (liegt im `data`-Ordner, übersteht Updates)

### Positionierung
HerdenPilot nicht als Ersatz für etablierte Programme, sondern als **Zusammenführer und Erinnerer**: Daten aus den bestehenden Systemen, daraus Warnungen und Auswertungen, die die einzelnen Portale nicht liefern.

---

## 7. Gesprächsleitfaden Vinzenz

**Betrieb**
1. Milchvieh, Mutterkuh, Mast oder gemischt? Wie viele Tiere, welche Rasse?
2. Welche Programme/Portale pflegst du heute (HI-Tier, LKV, Zuchtverband, Tierarzt …) — und was nervt dich daran am meisten?

**Zucht**
3. Wählst du Stiere gezielt aus? Nach welchen Kriterien (Zuchtwerte, Leichtkalbigkeit, Preis)?
4. Was willst du in ein paar Jahren wissen können — z. B. „welcher Stier bringt die besten Töchter"?
5. Besamungstechniker oder eigener Stier? Gesextes Sperma?

**Alltag**
6. Was hat beim Testen gefehlt — und was war überflüssig?
7. Wie trägst du lieber ein: Telegram im Stall, Handy-Browser oder abends am PC?
8. Gibt es eine Datei, die du ohnehin regelmäßig bekommst oder herunterlädst (Tierliste, MLP-Bericht, Abstammung)? **→ Beispiel mitbringen**, gern geschwärzt.

**Ergebnis des Gesprächs:** *(hier eintragen)*

---

## 8. Einen Schritt zurück — so geht's

**Grundsatz:** Nichts löschen, sondern zurücknehmen oder umbenennen — so bleibt jeder Schritt nachvollziehbar.

| Was | Wie |
|---|---|
| Eine Code-Änderung zurücknehmen | `git revert <commit>` — erzeugt einen Gegen-Commit, der Verlauf bleibt erhalten |
| hauspi auf älteren Stand | `cd ~/Tierkalb- && git checkout <commit> && docker compose up -d --build` |
| …und wieder zurück auf aktuell | `git checkout main && docker compose up -d --build` (vorher nötig, sonst klappt `/update` nicht) |
| Windows-exe auf ältere Version | ältere `HerdenPilot.exe` von der Releases-Seite, `data`-Ordner behalten |
| Daten wechseln (z. B. Demo ↔ Test) | Ordner umbenennen: `data` ↔ `data_demo`, vorher `docker compose down` — **nie `rm`** |
| Vor jedem größeren Schritt | in der App **CSV-Export** als zusätzliche Sicherung |

**Datenbank bei Versionswechsel:** Neue Spalten ergänzt HerdenPilot beim Start selbst; ältere Versionen ignorieren zusätzliche Spalten. Ein Schritt zurück ist für die Daten deshalb unkritisch.

---

## 9. Pflege dieses Dokuments

- **Jede Änderung:** Zeile im [Entwicklungsverlauf](#2-entwicklungsverlauf)
- **Jede Weichenstellung:** neue Entscheidung `E14`, `E15` … mit Warum, Verworfenem und Rückweg
- **Rückgängig gemachte Entscheidungen** nicht löschen — Status auf „verworfen" oder „ersetzt durch Exx" setzen
- **Fehler** mit Ursache und Lehre in [Fehler & Lehren](#4-fehler--lehren)
- **Erledigte Punkte** abhaken und mit Datum in den Verlauf übernehmen
