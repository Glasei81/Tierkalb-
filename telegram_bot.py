"""
telegram_bot.py — Telegram Bot für Tierkalb v3.0

Funktionen:
  - Täglich 6:00 Uhr: Geburten-Benachrichtigung
  - /status  — Vollständiger Status: Brunft, Trächtigkeit, Geburten
  - /hilfe   — Verfügbare Befehle
  - /start   — Begrüßung

Einrichtung: Token + Chat-ID in der App unter Einstellungen eintragen.
"""

import threading
import time
import requests
from datetime import date, timedelta


# ─── Telegram API Basis ────────────────────────────────────────────────────

def send_message(token: str, chat_id: str, text: str) -> bool:
    """Nachricht via Telegram Bot API senden."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(
            url,
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
        return r.ok
    except Exception as e:
        print(f"[Telegram] Sendefehler: {e}")
        return False


def get_updates(token: str, offset: int = 0) -> list:
    """Neue Nachrichten vom Bot abholen (Short Polling)."""
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        r = requests.get(
            url,
            params={"offset": offset, "timeout": 0, "limit": 10},
            timeout=10,
        )
        if r.ok:
            return r.json().get("result", [])
    except Exception:
        pass
    return []


# ─── Status-Nachricht aufbauen ────────────────────────────────────────────────

def build_status_message(farm_id: str, farm_name: str) -> str:
    import database as db

    heute = date.today()
    tiere = db.get_alle_tiere(farm_id)

    lines = [f"<b>🐄 Tierkalb — {farm_name}</b>"]
    lines.append(f"📅 {heute.strftime('%d.%m.%Y')}\n")

    # ─ Geburten bald (nächste 30 Tage) ─
    upcoming = db.get_upcoming_geburten(farm_id, days=30)
    if upcoming:
        lines.append("🤰 <b>GEBURTEN BALD:</b>")
        for u in upcoming:
            tage = u.get("tage_bis_geburt", 0)
            emoji = u.get("emoji", "🐄")
            name = u["name"]
            datum = u.get("erwartete_geburt_fmt", "")
            if tage <= 0:
                lines.append(f"  🔴 {emoji} <b>{name}</b> — heute erwartet!")
            elif tage == 1:
                lines.append(f"  🟠 {emoji} <b>{name}</b> — morgen ({datum})")
            elif tage <= 7:
                lines.append(f"  🟡 {emoji} {name} — in {tage} Tagen ({datum})")
            else:
                lines.append(f"  🟢 {emoji} {name} — in {tage} Tagen ({datum})")
        lines.append("")

    upcoming_namen = {u["name"] for u in upcoming}

    # ─ Pro Tier: Brunft / Besamung / Trächtigkeit analysieren ─
    brunft_faellig  = []   # Brunft steht bevor oder ist jetzt
    traechtig_liste = []   # Besamt, Geburt noch nicht erfolgt, nicht in upcoming
    nie_besamt      = []   # Noch gar keine Besamung eingetragen

    for tier in tiere:
        if not tier.get("tragzeit"):   # Hühner o.ä. überspringen
            continue

        lb  = db.get_letztes_ereignis(tier["id"], farm_id, "besamung")
        lbr = db.get_letztes_ereignis(tier["id"], farm_id, "brunft")
        lg  = db.get_letztes_ereignis(tier["id"], farm_id, "geburt")

        # Trächtig? → letzte Besamung liegt nach letzter Geburt (oder noch nie gekalbt)
        traechtig = False
        if lb:
            bes_datum = date.fromisoformat(lb["datum"])
            if lg:
                traechtig = date.fromisoformat(lg["datum"]) < bes_datum
            else:
                traechtig = True

        if traechtig:
            if tier["name"] not in upcoming_namen:
                bes_datum  = date.fromisoformat(lb["datum"])
                erw_geburt = bes_datum + timedelta(days=tier["tragzeit"])
                tage_seit  = (heute - bes_datum).days
                traechtig_liste.append({
                    "tier":      tier,
                    "bes_datum": bes_datum,
                    "erw":       erw_geburt,
                    "tage_seit": tage_seit,
                })
            continue

        # Brunft fällig?
        if lbr and tier.get("brunft_zyklus"):
            lbr_datum     = date.fromisoformat(lbr["datum"])
            naechste_brunft = lbr_datum + timedelta(days=tier["brunft_zyklus"])
            tage_bis      = (naechste_brunft - heute).days
            if tage_bis <= 5:   # innerhalb 5 Tagen oder überfällig
                brunft_faellig.append({
                    "tier":     tier,
                    "datum":    naechste_brunft,
                    "tage":     tage_bis,
                    "letztes_lb": lb,
                })
                continue

        # Noch nie besamt
        if not lb:
            nie_besamt.append({"tier": tier, "letztes_lbr": lbr})

    # ─ Ausgabe Brunft ─
    if brunft_faellig:
        lines.append("🌸 <b>BRUNFT / STIERIG:</b>")
        for b in brunft_faellig:
            t    = b["tier"]
            tage = b["tage"]
            dat  = b["datum"].strftime("%d.%m.%Y")
            em   = t.get("emoji", "🐄")
            lb   = b["letztes_lb"]

            if tage <= 0:
                zeile = f"  🔴 {em} <b>{t['name']}</b> — <b>jetzt stierig!</b>"
            elif tage <= 2:
                zeile = f"  🟠 {em} <b>{t['name']}</b> — in {tage} Tag(en) stierig ({dat})"
            else:
                zeile = f"  🟡 {em} {t['name']} — in {tage} Tagen stierig ({dat})"

            if lb:
                lb_dat    = date.fromisoformat(lb["datum"])
                tage_seit = (heute - lb_dat).days
                zeile    += f"\n    ↳ letzte Besamung: {lb_dat.strftime('%d.%m.%Y')} ({tage_seit} Tage her)"
            else:
                zeile += "\n    ↳ noch keine Besamung eingetragen"

            lines.append(zeile)
        lines.append("")

    # ─ Ausgabe Trächtig (ohne die, die sowieso schon in Geburten-Liste stehen) ─
    if traechtig_liste:
        lines.append("✅ <b>TRÄCHTIG:</b>")
        for b in traechtig_liste:
            t  = b["tier"]
            em = t.get("emoji", "🐄")
            erw = b["erw"].strftime("%d.%m.%Y")
            lines.append(
                f"  🟢 {em} {t['name']} — besamt {b['bes_datum'].strftime('%d.%m.%Y')}"
                f" ({b['tage_seit']} Tage) → Geburt ca. {erw}"
            )
        lines.append("")

    # ─ Noch nie besamt ─
    if nie_besamt:
        lines.append("❓ <b>NOCH NICHT BESAMT:</b>")
        for b in nie_besamt:
            t  = b["tier"]
            em = t.get("emoji", "🐄")
            lbr = b["letztes_lbr"]
            if lbr:
                lbr_dat = date.fromisoformat(lbr["datum"])
                lines.append(
                    f"  ⚪ {em} {t['name']} — letzte Brunft: {lbr_dat.strftime('%d.%m.%Y')}"
                )
            else:
                lines.append(f"  ⚪ {em} {t['name']} — noch keine Brunft eingetragen")
        lines.append("")

    # ─ Zusammenfassung ─
    monatskosten = db.get_kosten_pro_monat(farm_id, monate=1)
    mk = monatskosten[-1]["gesamt"] if monatskosten else 0.0

    lines.append("📊 <b>ÜBERSICHT:</b>")
    lines.append(f"  Tiere aktiv: {len(tiere)}")
    if mk > 0:
        lines.append(f"  Kosten diesen Monat: {mk:.0f} €")

    if not any([upcoming, brunft_faellig, traechtig_liste, nie_besamt]):
        lines.append("  Alles ruhig — keine dringenden Aktionen ✅")

    return "\n".join(lines)


# ─── Hilfe-Nachricht ────────────────────────────────────────────────────

def build_hilfe_message(farm_name: str) -> str:
    return (
        f"<b>🐄 Tierkalb — {farm_name}</b>\n\n"
        "Verfügbare Befehle:\n\n"
        "/status — Vollständiger Überblick\n"
        "   Brunft, Besamung, Trächtigkeit, Geburten\n\n"
        "/hilfe — Diese Hilfe\n\n"
        "<i>Täglich um 6:00 Uhr: Automatische Geburts-Benachrichtigung</i>"
    )


# ─── Befehl verarbeiten ────────────────────────────────────────────────────

def handle_command(text: str, farm_id: str, farm_name: str) -> str | None:
    cmd = text.strip().lower().split()[0]
    if cmd in ("/status",):
        return build_status_message(farm_id, farm_name)
    elif cmd in ("/hilfe", "/help", "/start"):
        return build_hilfe_message(farm_name)
    return None


# ─── Tägliche Morgen-Nachricht ──────────────────────────────────────────────

def send_daily_update(app):
    """Täglich 6:00 Uhr: Geburten-Übersicht + Hinweis auf /status."""
    with app.app_context():
        import database as db

        for farm in db.get_all_farms():
            fid      = farm["id"]
            token    = db.get_config(fid, "telegram_token", "")
            chat_id  = db.get_config(fid, "telegram_chat_id", "")
            if not token or not chat_id:
                continue

            upcoming = db.get_upcoming_geburten(fid, days=14)
            if not upcoming:
                continue

            lines = [f"<b>🌅 Guten Morgen! — {farm['name']}</b>"]
            lines.append("Geburten in den nächsten 14 Tagen:\n")
            for u in upcoming:
                tage  = u.get("tage_bis_geburt", 0)
                emoji = u.get("emoji", "🐄")
                name  = u["name"]
                datum = u.get("erwartete_geburt_fmt", "")
                if tage <= 0:
                    lines.append(f"🔴 {emoji} <b>{name}</b> — heute!")
                elif tage == 1:
                    lines.append(f"🟠 {emoji} <b>{name}</b> — morgen ({datum})")
                elif tage <= 3:
                    lines.append(f"🟡 {emoji} {name} — in {tage} Tagen ({datum})")
                else:
                    lines.append(f"🟢 {emoji} {name} — in {tage} Tagen ({datum})")
            lines.append("\n💡 Tipp: /status für vollständigen Überblick")
            send_message(token, chat_id, "\n".join(lines))


# ─── Polling-Thread ────────────────────────────────────────────────────

def polling_worker(app):
    """
    Läuft als Daemon-Thread.
    Alle 3 Sek.: neue Nachrichten abholen und Befehle beantworten.
    Alle 5 Min.:  Farm-Config neu laden (Token könnte nachträglich eingetragen werden).
    """
    import database as db

    offsets      = {}     # {token: letzter update_id + 1}
    config       = {}     # {token: {chat_id, farm_id, farm_name}}
    last_reload  = 0

    while True:
        now = time.time()

        # Config alle 5 Minuten neu laden
        if now - last_reload > 300:
            try:
                with app.app_context():
                    farms = db.get_all_farms()
                new_config = {}
                for farm in farms:
                    fid     = farm["id"]
                    with app.app_context():
                        token   = db.get_config(fid, "telegram_token", "")
                        chat_id = db.get_config(fid, "telegram_chat_id", "")
                    if token and chat_id:
                        new_config[token] = {
                            "chat_id":   chat_id,
                            "farm_id":   fid,
                            "farm_name": farm["name"],
                        }
                        if token not in offsets:
                            offsets[token] = 0
                config      = new_config
                last_reload = now
            except Exception as e:
                print(f"[Telegram] Config-Reload Fehler: {e}")

        # Nachrichten abholen
        for token, cfg in config.items():
            try:
                updates = get_updates(token, offsets.get(token, 0))
                for update in updates:
                    offsets[token] = update["update_id"] + 1
                    msg     = update.get("message", {})
                    text    = msg.get("text", "")
                    chat_id = str(msg.get("chat", {}).get("id", ""))

                    if not text or chat_id != cfg["chat_id"]:
                        continue

                    with app.app_context():
                        response = handle_command(
                            text, cfg["farm_id"], cfg["farm_name"]
                        )
                    if response:
                        send_message(token, chat_id, response)

            except Exception as e:
                print(f"[Telegram Polling] {e}")

        time.sleep(3)


# ─── Einstiegspunkt: Scheduler + Polling starten ───────────────────────────

def start_scheduler(app):
    """Wird beim App-Start aufgerufen. Startet Scheduler + Polling-Thread."""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler

        scheduler = BackgroundScheduler()
        scheduler.add_job(
            send_daily_update, "cron",
            hour=6, minute=0, args=[app],
            id="daily_update", replace_existing=True,
        )
        scheduler.start()
        print("[Telegram] Scheduler gestartet (täglich 6:00 Uhr)")

        t = threading.Thread(target=polling_worker, args=(app,), daemon=True)
        t.start()
        print("[Telegram] Polling-Thread gestartet")

        return scheduler

    except Exception as e:
        print(f"[Telegram] Start-Fehler: {e}")
        return None
