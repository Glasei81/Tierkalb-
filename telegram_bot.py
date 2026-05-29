"""
telegram_bot.py — Telegram Bot für Tierkalb v3.0

Ausgabe:
  - Täglich 6:00 Uhr: Geburten-Benachrichtigung
  - /status   — Vollständiger Überblick
  - /tiere    — Alle Tiere auflisten

Eingabe (direkt aus dem Stall):
  - /besamung <tier>             — Besamung heute eintragen
  - /brunft   <tier>             — Brunft heute eintragen
  - /geburt   <tier>             — Geburt heute eintragen
  - /impfung  <tier>             — Impfung heute eintragen
  - /tierarzt <tier> <betrag>    — Tierarzt-Kosten eintragen
  - /kosten   <tier> <betrag>    — Sonstige Kosten eintragen
  - /hilfe                       — Befehlsliste

Einrichtung: Token + Chat-ID in der App unter Einstellungen eintragen.
"""

import threading
import time
import requests
from datetime import date, timedelta


# ─── Telegram API Basis ──────────────────────────────────────────────────

def send_message(token: str, chat_id: str, text: str) -> bool:
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


# ─── Tier suchen (case-insensitiv, Teilstring) ────────────────────────────────────────────

def find_tier(tiere: list, suchname: str):
    s = suchname.lower().strip()
    exact = [t for t in tiere if t["name"].lower() == s]
    if exact:
        return exact[0], None
    partial = [t for t in tiere if s in t["name"].lower()]
    if len(partial) == 1:
        return partial[0], None
    if len(partial) > 1:
        return None, partial
    return None, None


def tier_nicht_gefunden(suchname: str, tiere: list) -> str:
    namen = ", ".join(t["name"] for t in tiere)
    return (
        f"❌ Tier <b>{suchname}</b> nicht gefunden.\n"
        f"Verfügbare Tiere: {namen}\n"
        f"Tipp: /tiere für die vollständige Liste."
    )


def datum_parsen(datum_str: str):
    s = datum_str.strip()
    heute = date.today()
    import datetime as _dt
    for fmt in ("%d.%m.%Y", "%d.%m.", "%Y-%m-%d"):
        try:
            parsed = _dt.datetime.strptime(s, fmt)
            if fmt == "%d.%m.":
                return date(heute.year, parsed.month, parsed.day)
            return parsed.date()
        except ValueError:
            continue
    return None


# ─── Befehle: Ausgabe ───────────────────────────────────────────────────────────────

def build_status_message(farm_id: str, farm_name: str) -> str:
    import database as db

    heute = date.today()
    tiere = db.get_alle_tiere(farm_id)

    lines = [f"<b>🐄 Tierkalb — {farm_name}</b>"]
    lines.append(f"📅 {heute.strftime('%d.%m.%Y')}\n")

    upcoming = db.get_upcoming_geburten(farm_id, days=30)
    if upcoming:
        lines.append("🤰 <b>GEBURTEN BALD:</b>")
        for u in upcoming:
            tage  = u.get("tage_bis_geburt", 0)
            emoji = u.get("emoji", "🐄")
            name  = u["name"]
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
    brunft_faellig  = []
    traechtig_liste = []
    nie_besamt      = []

    for tier in tiere:
        if not tier.get("tragzeit"):
            continue
        lb  = db.get_letztes_ereignis(tier["id"], farm_id, "besamung")
        lbr = db.get_letztes_ereignis(tier["id"], farm_id, "brunft")
        lg  = db.get_letztes_ereignis(tier["id"], farm_id, "geburt")

        traechtig = False
        if lb:
            bes_d = date.fromisoformat(lb["datum"])
            traechtig = (not lg) or date.fromisoformat(lg["datum"]) < bes_d

        if traechtig:
            if tier["name"] not in upcoming_namen:
                bes_d  = date.fromisoformat(lb["datum"])
                traechtig_liste.append({
                    "tier": tier, "bes_datum": bes_d,
                    "erw": bes_d + timedelta(days=tier["tragzeit"]),
                    "tage_seit": (heute - bes_d).days,
                })
            continue

        if lbr and tier.get("brunft_zyklus"):
            lbr_d = date.fromisoformat(lbr["datum"])
            naechste = lbr_d + timedelta(days=tier["brunft_zyklus"])
            if (naechste - heute).days <= 5:
                brunft_faellig.append({
                    "tier": tier, "datum": naechste,
                    "tage": (naechste - heute).days, "letztes_lb": lb,
                })
                continue

        if not lb:
            nie_besamt.append({"tier": tier, "letztes_lbr": lbr})

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
                zeile = f"  🟠 {em} <b>{t['name']}</b> — in {tage} Tag(en) ({dat})"
            else:
                zeile = f"  🟡 {em} {t['name']} — in {tage} Tagen ({dat})"
            if lb:
                lb_d = date.fromisoformat(lb["datum"])
                zeile += f"\n    ↳ letzte Besamung: {lb_d.strftime('%d.%m.%Y')} ({(heute - lb_d).days}d)"
            else:
                zeile += "\n    ↳ noch keine Besamung"
            lines.append(zeile)
        lines.append("")

    if traechtig_liste:
        lines.append("✅ <b>TRÄCHTIG:</b>")
        for b in traechtig_liste:
            t = b["tier"]
            lines.append(
                f"  🟢 {t.get('emoji','🐄')} {t['name']} — "
                f"besamt {b['bes_datum'].strftime('%d.%m.%Y')} ({b['tage_seit']}d) "
                f"→ Geburt ca. {b['erw'].strftime('%d.%m.%Y')}"
            )
        lines.append("")

    if nie_besamt:
        lines.append("❓ <b>NOCH NICHT BESAMT:</b>")
        for b in nie_besamt:
            t   = b["tier"]
            lbr = b["letztes_lbr"]
            suf = (f"letzte Brunft: {date.fromisoformat(lbr['datum']).strftime('%d.%m.%Y')}"
                   if lbr else "noch keine Brunft eingetragen")
            lines.append(f"  ⚪ {t.get('emoji','🐄')} {t['name']} — {suf}")
        lines.append("")

    mk = db.get_kosten_pro_monat(farm_id, monate=1)
    lines.append("📊 <b>ÜBERSICHT:</b>")
    lines.append(f"  Tiere aktiv: {len(tiere)}")
    if mk and mk[-1]["gesamt"] > 0:
        lines.append(f"  Kosten diesen Monat: {mk[-1]['gesamt']:.0f} €")
    if not any([upcoming, brunft_faellig, traechtig_liste, nie_besamt]):
        lines.append("  Alles ruhig — keine dringenden Aktionen ✅")
    lines.append("\n💡 Eingabe z.B.: /besamung Emma")
    return "\n".join(lines)


def build_tiere_message(tiere: list, farm_name: str) -> str:
    if not tiere:
        return "🐄 Noch keine Tiere eingetragen. Bitte in der App anlegen."
    lines = [f"<b>🐄 Tiere — {farm_name}:</b>\n"]
    for t in tiere:
        em  = t.get("emoji", "🐄")
        art = t.get("tierart_name") or ""
        oh  = f" [{t['ohrmarke']}]" if t.get("ohrmarke") else ""
        lines.append(f"  {em} <b>{t['name']}</b>{oh} — {art}")
    lines.append("\nEingabe z.B.: /besamung Emma")
    return "\n".join(lines)


def build_hilfe_message(farm_name: str) -> str:
    return (
        f"<b>🐄 Tierkalb — {farm_name}</b>\n\n"
        "<b>Abfragen:</b>\n"
        "/status — Brunft, Trächtigkeit, Geburten\n"
        "/tiere  — Alle Tiere auflisten\n\n"
        "<b>Eingabe (aus dem Stall):</b>\n"
        "/besamung Emma        — Besamung heute\n"
        "/besamung Emma 24.05. — Besamung mit Datum\n"
        "/brunft Emma          — Brunft heute\n"
        "/geburt Emma          — Geburt heute\n"
        "/impfung Emma         — Impfung heute\n"
        "/tierarzt Emma 150    — Tierarzt 150 €\n"
        "/kosten Emma 80       — Sonstige Kosten 80 €\n\n"
        "<i>Namen können abgekürzt werden: /besamung em findet Emma</i>\n"
        "<i>Täglich 6:00 Uhr: automatische Geburts-Meldung</i>"
    )


# ─── Befehle: Eingabe ───────────────────────────────────────────────────────────────

def cmd_ereignis(args: list, typ: str, farm_id: str) -> str:
    import database as db

    if not args:
        return f"❌ Bitte Tiernamen angeben. Beispiel: /{typ} Emma"

    tiere = db.get_alle_tiere(farm_id)
    heute = date.today()

    ereignis_datum = heute
    tiername_teile = args
    if len(args) >= 2:
        d = datum_parsen(args[-1])
        if d:
            ereignis_datum = d
            tiername_teile = args[:-1]

    suchname = " ".join(tiername_teile)
    tier, mehrere = find_tier(tiere, suchname)

    if mehrere:
        namen = ", ".join(t["name"] for t in mehrere)
        return f"❓ Mehrere Tiere gefunden: {namen}\nBitte genauer angeben."
    if not tier:
        return tier_nicht_gefunden(suchname, tiere)

    db.add_ereignis(farm_id, tier["id"], typ, ereignis_datum.isoformat())

    emoji  = tier.get("emoji", "🐄")
    dat_fmt = ereignis_datum.strftime("%d.%m.%Y")
    labels  = {
        "besamung": "💉 Besamung",
        "brunft":   "🌸 Brunft",
        "geburt":   "🐣 Geburt",
        "impfung":  "💊 Impfung",
    }
    label = labels.get(typ, typ.capitalize())
    antwort = f"✅ {label} für <b>{tier['name']}</b> eingetragen ({dat_fmt})."

    if typ == "besamung" and tier.get("tragzeit"):
        erw = ereignis_datum + timedelta(days=tier["tragzeit"])
        antwort += f"\n📅 Erwartete Geburt: <b>{erw.strftime('%d.%m.%Y')}</b>"

    if typ == "brunft" and tier.get("brunft_zyklus"):
        naechste = ereignis_datum + timedelta(days=tier["brunft_zyklus"])
        antwort += f"\n📅 Nächste Brunft ca.: {naechste.strftime('%d.%m.%Y')}"

    return antwort


def cmd_kosten(args: list, typ: str, farm_id: str) -> str:
    import database as db

    if len(args) < 2:
        cmd   = "tierarzt" if typ == "Tierarzt" else "kosten"
        return f"❌ Bitte Tier und Betrag angeben. Beispiel: /{cmd} Emma 150"

    tiere = db.get_alle_tiere(farm_id)
    heute = date.today()

    betrag_str = args[-1].replace(",", ".")
    try:
        betrag = float(betrag_str)
    except ValueError:
        return f"❌ Betrag nicht erkannt: <b>{args[-1]}</b>\nBeispiel: /tierarzt Emma 150.50"

    suchname = " ".join(args[:-1])
    tier, mehrere = find_tier(tiere, suchname)

    if mehrere:
        namen = ", ".join(t["name"] for t in mehrere)
        return f"❓ Mehrere Tiere gefunden: {namen}\nBitte genauer angeben."
    if not tier:
        return tier_nicht_gefunden(suchname, tiere)

    db.add_kosten(farm_id, tier["id"], typ, betrag, heute.isoformat())

    return (
        f"✅ {typ} <b>{betrag:.2f} €</b> für <b>{tier['name']}</b> "
        f"eingetragen ({heute.strftime('%d.%m.%Y')})."
    )


# ─── Befehl-Router ─────────────────────────────────────────────────────────────────

def handle_command(text: str, farm_id: str, farm_name: str):
    import database as db

    parts = text.strip().split()
    if not parts:
        return None

    cmd  = parts[0].lower().split("@")[0]
    args = parts[1:]

    if cmd == "/status":
        return build_status_message(farm_id, farm_name)
    elif cmd == "/tiere":
        tiere = db.get_alle_tiere(farm_id)
        return build_tiere_message(tiere, farm_name)
    elif cmd in ("/hilfe", "/help", "/start"):
        return build_hilfe_message(farm_name)
    elif cmd == "/besamung":
        return cmd_ereignis(args, "besamung", farm_id)
    elif cmd == "/brunft":
        return cmd_ereignis(args, "brunft", farm_id)
    elif cmd == "/geburt":
        return cmd_ereignis(args, "geburt", farm_id)
    elif cmd == "/impfung":
        return cmd_ereignis(args, "impfung", farm_id)
    elif cmd == "/tierarzt":
        return cmd_kosten(args, "Tierarzt", farm_id)
    elif cmd == "/kosten":
        return cmd_kosten(args, "Sonstiges", farm_id)

    return None


# ─── Tägliche Morgen-Nachricht ────────────────────────────────────────────────────────

def send_daily_update(app):
    with app.app_context():
        import database as db
        for farm in db.get_all_farms():
            fid     = farm["id"]
            token   = db.get_config(fid, "telegram_token", "")
            chat_id = db.get_config(fid, "telegram_chat_id", "")
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
            lines.append("\n💡 /status für vollständigen Überblick")
            send_message(token, chat_id, "\n".join(lines))


# ─── Polling-Thread ────────────────────────────────────────────────────────────────

def polling_worker(app):
    import database as db

    offsets     = {}
    config      = {}
    last_reload = 0

    while True:
        now = time.time()

        if now - last_reload > 300:
            try:
                with app.app_context():
                    farms = db.get_all_farms()
                new_cfg = {}
                for farm in farms:
                    fid = farm["id"]
                    with app.app_context():
                        token   = db.get_config(fid, "telegram_token", "")
                        chat_id = db.get_config(fid, "telegram_chat_id", "")
                    if token and chat_id:
                        new_cfg[token] = {
                            "chat_id":   chat_id,
                            "farm_id":   fid,
                            "farm_name": farm["name"],
                        }
                        if token not in offsets:
                            offsets[token] = 0
                config      = new_cfg
                last_reload = now
            except Exception as e:
                print(f"[Telegram] Config-Reload: {e}")

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


# ─── Start ────────────────────────────────────────────────────────────────────────

def start_scheduler(app):
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
