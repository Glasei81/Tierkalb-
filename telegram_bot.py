"""
telegram_bot.py — Telegram Bot für HerdenPilot v3.3
"""

import re
import threading
import time
import smtplib
from email.mime.text import MIMEText

import requests
from datetime import date, timedelta

TK_FENSTER = 7

_TK_TAGE = {
    "Rinder":   28,
    "Schafe":   20,
    "Schweine": 21,
    "Ziegen":   20,
}


def _strip_html(text: str) -> str:
    return re.sub(r'<[^>]+>', '', text)


def send_message(token: str, chat_id: str, text: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
        return r.ok
    except Exception as e:
        print(f"[Telegram] Sendefehler: {e}")
        return False


def send_ntfy(topic: str, message: str, server: str = "ntfy.sh") -> bool:
    if not topic:
        return False
    server = server.strip().strip("/")
    topic  = topic.strip().strip("/")
    url = f"https://{server}/{topic}"
    try:
        r = requests.post(
            url,
            data=_strip_html(message).encode("utf-8"),
            headers={"Title": "HerdenPilot", "Tags": "cow"},
            timeout=10,
        )
        return r.ok
    except Exception as e:
        print(f"[ntfy] Sendefehler: {e}")
        return False


def send_email_notification(smtp_host: str, port: str, user: str,
                             password: str, to: str, subject: str, body: str) -> bool:
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = user
        msg["To"] = to
        with smtplib.SMTP(smtp_host, int(port)) as srv:
            srv.ehlo()
            srv.starttls()
            srv.login(user, password)
            srv.send_message(msg)
        return True
    except Exception as e:
        print(f"[Email] Sendefehler: {e}")
        return False


def get_updates(token: str, offset: int = 0) -> list:
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        r = requests.get(url, params={"offset": offset, "timeout": 0, "limit": 10}, timeout=10)
        if r.ok:
            return r.json().get("result", [])
    except Exception:
        pass
    return []


def set_bot_commands(token: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/setMyCommands"
    commands = [
        {"command": "status",     "description": "Brunft, Trächtigkeit, Geburten, TK-Kontrolle"},
        {"command": "tiere",      "description": "Alle Tiere auflisten"},
        {"command": "neues_tier", "description": "Neues Tier anlegen: /neues_tier Name Tierart"},
        {"command": "besamung",   "description": "Besamung: /besamung Emma [Datum] [Kosten €]"},
        {"command": "brunft",     "description": "Brunft eintragen: /brunft Emma"},
        {"command": "geburt",     "description": "Geburt eintragen: /geburt Emma"},
        {"command": "impfung",    "description": "Impfung eintragen: /impfung Emma"},
        {"command": "tierarzt",   "description": "Tierarzt-Kosten: /tierarzt Emma 150"},
        {"command": "kosten",     "description": "Sonstige Kosten: /kosten Emma 80"},
        {"command": "hilfe",      "description": "Alle Befehle anzeigen"},
    ]
    try:
        r = requests.post(url, json={"commands": commands}, timeout=10)
        return r.ok
    except Exception as e:
        print(f"[Telegram] setMyCommands Fehler: {e}")
        return False


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
    return f"❌ Tier <b>{suchname}</b> nicht gefunden.\nVerfügbare Tiere: {namen}\nTipp: /tiere für die vollständige Liste."


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


def build_tk_liste(farm_id: str) -> list:
    import database as db
    heute = date.today()
    tiere = db.get_alle_tiere(farm_id)
    result = []
    for tier in tiere:
        if tier.get("geschlecht") == "männlich":
            continue
        if not tier.get("tragzeit"):
            continue
        tk_tage = _TK_TAGE.get(tier.get("tierart_name", ""), 0)
        if not tk_tage:
            continue
        lb = db.get_letztes_ereignis(tier["id"], farm_id, "besamung")
        if not lb:
            continue
        bes_d = date.fromisoformat(lb["datum"])
        tage_seit = (heute - bes_d).days
        if not (tk_tage <= tage_seit <= tk_tage + TK_FENSTER):
            continue
        lb_brunft = db.get_letztes_ereignis(tier["id"], farm_id, "brunft")
        if lb_brunft and date.fromisoformat(lb_brunft["datum"]) > bes_d:
            continue
        lb_geburt = db.get_letztes_ereignis(tier["id"], farm_id, "geburt")
        if lb_geburt and date.fromisoformat(lb_geburt["datum"]) > bes_d:
            continue
        result.append({"tier": tier, "bes_datum": bes_d, "tage_seit": tage_seit, "tk_tage": tk_tage})
    return result


def build_status_message(farm_id: str, farm_name: str) -> str:
    import database as db
    heute = date.today()
    tiere = db.get_alle_tiere(farm_id)
    lines = [f"<b>🐄 HerdenPilot — {farm_name}</b>", f"📅 {heute.strftime('%d.%m.%Y')}\n"]

    upcoming = db.get_upcoming_geburten(farm_id, days=30)
    if upcoming:
        lines.append("🤰 <b>GEBURTEN BALD:</b>")
        for u in upcoming:
            tage = u.get("tage_bis_geburt", 0)
            em = u.get("emoji", "🐄")
            name = u["name"]
            datum = u.get("erwartete_geburt_fmt", "")
            if tage <= 0:   lines.append(f"  🔴 {em} <b>{name}</b> — heute erwartet!")
            elif tage == 1: lines.append(f"  🟠 {em} <b>{name}</b> — morgen ({datum})")
            elif tage <= 7: lines.append(f"  🟡 {em} {name} — in {tage} Tagen ({datum})")
            else:           lines.append(f"  🟢 {em} {name} — in {tage} Tagen ({datum})")
        lines.append("")

    tk_liste = build_tk_liste(farm_id)
    if tk_liste:
        lines.append("🔬 <b>TRÄCHTIGKEITSKONTROLLE FÄLLIG:</b>")
        for tk in tk_liste:
            t = tk["tier"]
            lines.append(
                f"  🔬 {t.get('emoji','🐄')} <b>{t['name']}</b> — besamt {tk['bes_datum'].strftime('%d.%m.%Y')} ({tk['tage_seit']}d)\n"
                f"    ↳ Trächtig? Wenn nein: /brunft {t['name']}"
            )
        lines.append("")

    upcoming_namen = {u["name"] for u in upcoming}
    brunft_faellig = []
    traechtig_liste = []
    nie_besamt = []

    for tier in tiere:
        if tier.get("geschlecht") == "männlich":
            continue
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
                bes_d = date.fromisoformat(lb["datum"])
                traechtig_liste.append({"tier": tier, "bes_datum": bes_d,
                    "erw": bes_d + timedelta(days=tier["tragzeit"]),
                    "tage_seit": (heute - bes_d).days})
            continue
        if lbr and tier.get("brunft_zyklus"):
            lbr_d = date.fromisoformat(lbr["datum"])
            naechste = lbr_d + timedelta(days=tier["brunft_zyklus"])
            if (naechste - heute).days <= 7:
                brunft_faellig.append({"tier": tier, "datum": naechste,
                    "tage": (naechste - heute).days, "letztes_lb": lb})
                continue
        if not lb:
            nie_besamt.append({"tier": tier, "letztes_lbr": lbr})

    if brunft_faellig:
        lines.append("🌸 <b>BRUNFT / STIERIG:</b>")
        for b in brunft_faellig:
            t = b["tier"]; tage = b["tage"]; dat = b["datum"].strftime("%d.%m.%Y"); em = t.get("emoji", "🐄"); lb = b["letztes_lb"]
            if tage <= 0:
                zeile = f"  🔴 {em} <b>{t['name']}</b> — <b>jetzt stierig!</b>"
                zeile += f"\n    ↳ Besamungsfenster bis ca. {(heute + timedelta(days=2)).strftime('%d.%m.')} — Besamer anrufen!"
            elif tage <= 3:
                zeile = f"  🟠 {em} <b>{t['name']}</b> — in {tage} Tag(en) stierig ({dat})"
                zeile += f"\n    ↳ ⚠️ Besamer jetzt bestellen!"
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
            lines.append(f"  🟢 {t.get('emoji','🐄')} {t['name']} — besamt {b['bes_datum'].strftime('%d.%m.%Y')} ({b['tage_seit']}d) → Geburt ca. {b['erw'].strftime('%d.%m.%Y')}")
        lines.append("")

    if nie_besamt:
        lines.append("❓ <b>NOCH NICHT BESAMT:</b>")
        for b in nie_besamt:
            t = b["tier"]; lbr = b["letztes_lbr"]
            suf = (f"letzte Brunft: {date.fromisoformat(lbr['datum']).strftime('%d.%m.%Y')}" if lbr else "noch keine Brunft eingetragen")
            lines.append(f"  ⚪ {t.get('emoji','🐄')} {t['name']} — {suf}")
        lines.append("")

    impfungen_faellig = db.get_faellige_impfungen(farm_id)
    if impfungen_faellig:
        lines.append("💊 <b>IMPFUNG FÄLLIG:</b>")
        for imp in impfungen_faellig:
            em = imp.get("emoji", "🐄"); name = imp["name"]; letzte = imp.get("letzte_impfung")
            if letzte:
                lines.append(f"  💊 {em} {name} — letzte Impfung vor {int(imp.get('tage_seit_impfung') or 0)} Tagen")
            else:
                lines.append(f"  💊 {em} {name} — noch nie geimpft")
        lines.append("")

    mk = db.get_kosten_pro_monat(farm_id, monate=1)
    lines.append("📊 <b>ÜBERSICHT:</b>")
    lines.append(f"  Tiere aktiv: {len(tiere)}")
    if mk and mk[-1]["gesamt"] > 0:
        lines.append(f"  Kosten diesen Monat: {mk[-1]['gesamt']:.0f} €")
    if not any([upcoming, tk_liste, brunft_faellig, traechtig_liste, nie_besamt, impfungen_faellig]):
        lines.append("  Alles ruhig — keine dringenden Aktionen ✅")
    lines.append("\n💡 Eingabe z.B.: /besamung Emma")
    return "\n".join(lines)


def build_tiere_message(tiere: list, farm_name: str) -> str:
    if not tiere:
        return "🐄 Noch keine Tiere eingetragen. Bitte in der App anlegen."
    lines = [f"<b>🐄 Tiere — {farm_name}:</b>\n"]
    for t in tiere:
        em = t.get("emoji", "🐄"); art = t.get("tierart_name") or ""
        oh = f" [{t['ohrmarke']}]" if t.get("ohrmarke") else ""
        geschlecht = " (♂)" if t.get("geschlecht") == "männlich" else ""
        lines.append(f"  {em} <b>{t['name']}</b>{oh}{geschlecht} — {art}")
    lines.append("\nEingabe z.B.: /besamung Emma")
    return "\n".join(lines)


def build_hilfe_message(farm_name: str) -> str:
    return (
        f"<b>🐄 HerdenPilot — {farm_name}</b>\n\n"
        "<b>Abfragen:</b>\n/status — Brunft, Trächtigkeit, Geburten, TK-Kontrolle\n/tiere  — Alle Tiere auflisten\n\n"
        "<b>Neues Tier anlegen:</b>\n/neues_tier Emma Rind     — Kuh namens Emma anlegen\n/neues_tier Wolke Schaf   — Schaf namens Wolke anlegen\n\n"
        "<b>Eingabe (aus dem Stall):</b>\n"
        "/besamung Emma            — Besamung heute\n/besamung Emma 85         — Besamung + 85 € Kosten\n"
        "/besamung Emma 24.05. 85  — Besamung mit Datum + Kosten\n/brunft Emma              — Brunft heute\n"
        "/geburt Emma              — Geburt heute\n/impfung Emma             — Impfung heute\n"
        "/tierarzt Emma 150        — Tierarzt 150 €\n/kosten Emma 80           — Sonstige Kosten 80 €\n\n"
        "<b>Trächtigkeitskontrolle:</b>\nErscheint automatisch in /status wenn die Kontrolle fällig ist.\n"
        "War die Kontrolle negativ → /brunft Emma\n\n"
        "<i>Namen können abgekürzt werden: /besamung em findet Emma</i>\n"
        "<i>Täglich 6:00 Uhr: automatische Geburts-, TK- und Impfmeldung</i>"
    )


def cmd_neues_tier(args: list, farm_id: str) -> str:
    import database as db
    tierarten = db.get_tierarten(farm_id)
    tierart_liste = " | ".join(f"{ta['emoji']}{ta['name']}" for ta in tierarten)
    if len(args) < 2:
        return f"❌ Bitte Name und Tierart angeben.\nBeispiel: /neues_tier Emma Rind\n\nVerfügbare Tierarten:\n{tierart_liste}"
    tierart_suche = args[-1].lower()
    name = " ".join(args[:-1]).strip()
    tierart = None
    for ta in tierarten:
        if tierart_suche in ta["name"].lower() or ta["name"].lower().startswith(tierart_suche):
            tierart = ta; break
    if not tierart:
        return f"❌ Tierart '{args[-1]}' nicht gefunden.\nVerfügbare Tierarten: {tierart_liste}"
    db.add_tier(farm_id, name, "", tierart["id"], None, "weiblich", "")
    return f"✅ {tierart['emoji']} <b>{name}</b> wurde angelegt.\nTierart: {tierart['name']}\n📝 Ohrmarke, Geburtsdatum und Geschlecht kannst du in der App ergänzen."


def cmd_besamung(args: list, farm_id: str) -> str:
    import database as db
    if not args:
        return "❌ Bitte Tiernamen angeben. Beispiel: /besamung Emma"
    tiere = db.get_alle_tiere(farm_id)
    heute = date.today()
    ereignis_datum = heute; kosten = None; teile = list(args)
    if len(teile) >= 2:
        try: kosten = float(teile[-1].replace(",", ".")); teile = teile[:-1]
        except ValueError: pass
    if len(teile) >= 2:
        d = datum_parsen(teile[-1])
        if d: ereignis_datum = d; teile = teile[:-1]
    suchname = " ".join(teile)
    tier, mehrere = find_tier(tiere, suchname)
    if mehrere:
        return f"❓ Mehrere Tiere gefunden: {', '.join(t['name'] for t in mehrere)}\nBitte genauer angeben."
    if not tier:
        return tier_nicht_gefunden(suchname, tiere)
    if tier.get("geschlecht") == "männlich":
        return f"❌ <b>{tier['name']}</b> ist männlich — Besamung nicht möglich."
    db.add_ereignis(farm_id, tier["id"], "besamung", ereignis_datum.isoformat())
    dat_fmt = ereignis_datum.strftime("%d.%m.%Y")
    antwort = f"✅ 💉 Besamung für <b>{tier['name']}</b> eingetragen ({dat_fmt})."
    if kosten is not None:
        db.add_kosten(farm_id, tier["id"], "Besamung", kosten, ereignis_datum.isoformat())
        antwort += f"\n💶 Kosten <b>{kosten:.2f} €</b> eingetragen."
    if tier.get("tragzeit"):
        erw = ereignis_datum + timedelta(days=tier["tragzeit"])
        antwort += f"\n📅 Erwartete Geburt: <b>{erw.strftime('%d.%m.%Y')}</b>"
    tk_tage = _TK_TAGE.get(tier.get("tierart_name", ""), 0)
    if tk_tage:
        tk_datum = ereignis_datum + timedelta(days=tk_tage)
        antwort += f"\n🔬 Trächtigkeitskontrolle: ab <b>{tk_datum.strftime('%d.%m.%Y')}</b>"
    return antwort


def cmd_ereignis(args: list, typ: str, farm_id: str) -> str:
    import database as db
    if not args:
        return f"❌ Bitte Tiernamen angeben. Beispiel: /{typ} Emma"
    tiere = db.get_alle_tiere(farm_id)
    heute = date.today()
    ereignis_datum = heute; tiername_teile = args
    if len(args) >= 2:
        d = datum_parsen(args[-1])
        if d: ereignis_datum = d; tiername_teile = args[:-1]
    suchname = " ".join(tiername_teile)
    tier, mehrere = find_tier(tiere, suchname)
    if mehrere:
        return f"❓ Mehrere Tiere gefunden: {', '.join(t['name'] for t in mehrere)}\nBitte genauer angeben."
    if not tier:
        return tier_nicht_gefunden(suchname, tiere)
    if typ in ("brunft", "besamung") and tier.get("geschlecht") == "männlich":
        return f"❌ <b>{tier['name']}</b> ist männlich — {typ.capitalize()} nicht möglich."
    db.add_ereignis(farm_id, tier["id"], typ, ereignis_datum.isoformat())
    dat_fmt = ereignis_datum.strftime("%d.%m.%Y")
    labels = {"besamung": "💉 Besamung", "brunft": "🌸 Brunft", "geburt": "🐣 Geburt", "impfung": "💊 Impfung"}
    label = labels.get(typ, typ.capitalize())
    antwort = f"✅ {label} für <b>{tier['name']}</b> eingetragen ({dat_fmt})."
    if typ == "brunft" and tier.get("brunft_zyklus"):
        naechste = ereignis_datum + timedelta(days=tier["brunft_zyklus"])
        antwort += f"\n📅 Nächste Brunft ca.: {naechste.strftime('%d.%m.%Y')}"
    return antwort


def cmd_kosten(args: list, typ: str, farm_id: str) -> str:
    import database as db
    if len(args) < 2:
        cmd = "tierarzt" if typ == "Tierarzt" else "kosten"
        return f"❌ Bitte Tier und Betrag angeben. Beispiel: /{cmd} Emma 150"
    tiere = db.get_alle_tiere(farm_id)
    heute = date.today()
    betrag_str = args[-1].replace(",", ".")
    try: betrag = float(betrag_str)
    except ValueError: return f"❌ Betrag nicht erkannt: <b>{args[-1]}</b>\nBeispiel: /tierarzt Emma 150.50"
    suchname = " ".join(args[:-1])
    tier, mehrere = find_tier(tiere, suchname)
    if mehrere:
        return f"❓ Mehrere Tiere gefunden: {', '.join(t['name'] for t in mehrere)}\nBitte genauer angeben."
    if not tier:
        return tier_nicht_gefunden(suchname, tiere)
    db.add_kosten(farm_id, tier["id"], typ, betrag, heute.isoformat())
    return f"✅ {typ} <b>{betrag:.2f} €</b> für <b>{tier['name']}</b> eingetragen ({heute.strftime('%d.%m.%Y')})."


def handle_command(text: str, farm_id: str, farm_name: str):
    import database as db
    parts = text.strip().split()
    if not parts: return None
    cmd = parts[0].lower().split("@")[0]; args = parts[1:]
    if cmd == "/status":     return build_status_message(farm_id, farm_name)
    elif cmd == "/tiere":    return build_tiere_message(db.get_alle_tiere(farm_id), farm_name)
    elif cmd in ("/hilfe", "/help", "/start"): return build_hilfe_message(farm_name)
    elif cmd == "/neues_tier": return cmd_neues_tier(args, farm_id)
    elif cmd == "/besamung":   return cmd_besamung(args, farm_id)
    elif cmd == "/brunft":     return cmd_ereignis(args, "brunft", farm_id)
    elif cmd == "/geburt":     return cmd_ereignis(args, "geburt", farm_id)
    elif cmd == "/impfung":    return cmd_ereignis(args, "impfung", farm_id)
    elif cmd == "/tierarzt":   return cmd_kosten(args, "Tierarzt", farm_id)
    elif cmd == "/kosten":     return cmd_kosten(args, "Sonstiges", farm_id)
    return None


def send_daily_update(app):
    with app.app_context():
        import database as db
        for farm in db.get_all_farms():
            fid = farm["id"]
            upcoming  = db.get_upcoming_geburten(fid, days=14)
            tk_liste  = build_tk_liste(fid)
            impfungen = db.get_faellige_impfungen(fid)
            if not upcoming and not tk_liste and not impfungen:
                continue

            lines = [f"<b>🌅 Guten Morgen! — {farm['name']}</b>"]
            if upcoming:
                lines.append("\nGeburten in den nächsten 14 Tagen:")
                for u in upcoming:
                    tage = u.get("tage_bis_geburt", 0); em = u.get("emoji", "🐄"); name = u["name"]; datum = u.get("erwartete_geburt_fmt", "")
                    if tage <= 0:   lines.append(f"🔴 {em} <b>{name}</b> — heute!")
                    elif tage == 1: lines.append(f"🟠 {em} <b>{name}</b> — morgen ({datum})")
                    elif tage <= 3: lines.append(f"🟡 {em} {name} — in {tage} Tagen ({datum})")
                    else:           lines.append(f"🟢 {em} {name} — in {tage} Tagen ({datum})")
            if tk_liste:
                lines.append("\n🔬 <b>Trächtigkeitskontrolle fällig:</b>")
                for tk in tk_liste:
                    t = tk["tier"]
                    lines.append(f"  {t.get('emoji','🐄')} <b>{t['name']}</b> — besamt {tk['bes_datum'].strftime('%d.%m.%Y')} ({tk['tage_seit']}d)")
            if impfungen:
                lines.append("\n💊 <b>Impfungen fällig:</b>")
                for imp in impfungen:
                    em = imp.get("emoji", "🐄"); letzte = imp.get("letzte_impfung")
                    if letzte: lines.append(f"  {em} {imp['name']} — letzte Impfung vor {int(imp.get('tage_seit_impfung') or 0)} Tagen")
                    else:      lines.append(f"  {em} {imp['name']} — noch nie geimpft")
            lines.append("\n💡 /status für vollständigen Überblick")
            html_msg = "\n".join(lines)

            # Telegram
            token   = db.get_config(fid, "telegram_token", "")
            chat_id = db.get_config(fid, "telegram_chat_id", "")
            if token and chat_id and db.get_config(fid, "notify_telegram", "1") == "1":
                send_message(token, chat_id, html_msg)

            # ntfy.sh
            ntfy_topic  = db.get_config(fid, "ntfy_topic", "")
            ntfy_server = db.get_config(fid, "ntfy_server", "ntfy.sh")
            if ntfy_topic and db.get_config(fid, "notify_ntfy", "0") == "1":
                send_ntfy(ntfy_topic, html_msg, ntfy_server)

            # E-Mail
            if db.get_config(fid, "notify_email", "0") == "1":
                smtp = db.get_config(fid, "email_smtp", "")
                port = db.get_config(fid, "email_port", "587")
                user = db.get_config(fid, "email_user", "")
                pw   = db.get_config(fid, "email_password", "")
                to   = db.get_config(fid, "email_to", "")
                if smtp and user and pw and to:
                    send_email_notification(
                        smtp, port, user, pw, to,
                        f"🐄 HerdenPilot — {farm['name']}",
                        _strip_html(html_msg),
                    )


def polling_worker(app):
    import database as db
    offsets = {}; config = {}; commands_set = set(); last_reload = 0
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
                        new_cfg[token] = {"chat_id": chat_id, "farm_id": fid, "farm_name": farm["name"]}
                        if token not in offsets: offsets[token] = 0
                        if token not in commands_set:
                            if set_bot_commands(token): commands_set.add(token)
                config = new_cfg; last_reload = now
            except Exception as e:
                print(f"[Telegram] Config-Reload: {e}")
        for token, cfg in config.items():
            try:
                updates = get_updates(token, offsets.get(token, 0))
                for update in updates:
                    offsets[token] = update["update_id"] + 1
                    msg = update.get("message", {}); text = msg.get("text", "")
                    chat_id = str(msg.get("chat", {}).get("id", ""))
                    if not text or chat_id != cfg["chat_id"]: continue
                    with app.app_context():
                        response = handle_command(text, cfg["farm_id"], cfg["farm_name"])
                    if response: send_message(token, chat_id, response)
            except Exception as e:
                print(f"[Telegram Polling] {e}")
        time.sleep(3)


def start_scheduler(app):
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler(timezone="Europe/Berlin")
        scheduler.add_job(send_daily_update, "cron", hour=6, minute=0, args=[app], id="daily_update", replace_existing=True)
        scheduler.start()
        print("[Telegram] Scheduler gestartet (täglich 6:00 Uhr Europe/Berlin)")
        t = threading.Thread(target=polling_worker, args=(app,), daemon=True)
        t.start()
        print("[Telegram] Polling-Thread gestartet")
        return scheduler
    except Exception as e:
        print(f"[Telegram] Start-Fehler: {e}")
        return None
