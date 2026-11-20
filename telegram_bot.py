"""
telegram_bot.py — Telegram Bot für HerdenPilot v3.3
"""

import re
import threading
import time
import smtplib
from email.mime.text import MIMEText

import requests
import updater
import html as _html
from datetime import date, timedelta

import fruchtbarkeit as fb


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
        {"command": "status",     "description": "Termine: Stierigkeit, Untersuchung, Kalbung"},
        {"command": "tiere",      "description": "Alle Tiere auflisten"},
        {"command": "neues_tier", "description": "Neues Tier anlegen: /neues_tier Name Tierart"},
        {"command": "besamung",   "description": "Besamung: /besamung Emma [Datum] [Kosten €]"},
        {"command": "brunft",     "description": "Brunft eintragen: /brunft Emma"},
        {"command": "geburt",     "description": "Geburt eintragen: /geburt Emma"},
        {"command": "tk",         "description": "Trächtigkeitsuntersuchung: /tk Emma ja|nein"},
        {"command": "tierarzt",   "description": "Tierarzt/Impfung-Kosten: /tierarzt Emma 150"},
        {"command": "kosten",     "description": "Sonstige Kosten: /kosten Emma 80"},
        {"command": "hilfe",      "description": "Alle Befehle anzeigen"},
        {"command": "version",    "description": "Auf neue Version prüfen"},
        {"command": "update",     "description": "HerdenPilot aktualisieren"},
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


_ICON = {"nachbesamen": "🔴", "kontrolle": "👀", "tu": "🔬", "tk_fehlt": "⚠️",
         "kalbung": "🐣", "kalbung_ueberfaellig": "⚠️", "brunft": "🌸"}
_GRUPPEN_TITEL = {"ueberfaellig": "⚠️ <b>ÜBERFÄLLIG</b>", "heute": "📌 <b>HEUTE</b>",
                  "woche": "📅 <b>NÄCHSTE 7 TAGE</b>", "spaeter": "🗓 <b>SPÄTER</b>"}


def _termin_zeile(tm, heute) -> str:
    name = _html.escape(tm["tier"]["name"])
    return (f"  {_ICON.get(tm['art'], '•')} <b>{name}</b> — {tm['text']}"
            f" · {tm['datum'].strftime('%d.%m.')}, {fb.wann(tm, heute)}")


def _termin_bloecke(farm_id: str, heute, gruppen: list, spaeter_max: int = 6):
    """Termine eines Betriebs als Textblöcke. Rückgabe: tiere, ablauf je Tier, Zeilen."""
    import database as db
    tiere = db.get_alle_tiere(farm_id)
    abl, termine = fb.herde(tiere, db.get_ereignisse_je_tier(farm_id), heute)
    g = fb.gruppieren(termine, heute)
    lines = []
    for key in gruppen:
        liste = g[key]
        if not liste:
            continue
        lines.append(_GRUPPEN_TITEL[key])
        zeigen = liste[:spaeter_max] if key == "spaeter" else liste
        lines += [_termin_zeile(tm, heute) for tm in zeigen]
        if len(liste) > len(zeigen):
            lines.append(f"  … und {len(liste) - len(zeigen)} weitere (siehe App)")
        lines.append("")
    return tiere, abl, lines


def build_status_message(farm_id: str, farm_name: str) -> str:
    import database as db
    heute = date.today()
    tiere, abl, termin_zeilen = _termin_bloecke(
        farm_id, heute, ["ueberfaellig", "heute", "woche", "spaeter"])
    lines = [f"<b>🐄 HerdenPilot — {farm_name}</b>", f"📅 {heute.strftime('%d.%m.%Y')}\n"]
    lines += termin_zeilen or ["Keine anstehenden Termine ✅\n"]

    st = [a["status"] for a in abl.values() if a["status"]]
    unbestaetigt = st.count("traechtig_angenommen")
    lines.append("📊 <b>ÜBERSICHT:</b>")
    lines.append(f"  Tiere aktiv: {len(tiere)}")
    lines.append(f"  Trächtig: {st.count('traechtig')}"
                 + (f" (+{unbestaetigt} ohne Untersuchung)" if unbestaetigt else ""))
    lines.append(f"  Besamt, Ergebnis offen: {st.count('besamt') + st.count('tk_fehlt')}")
    lines.append(f"  Offen / nicht trächtig: {st.count('offen') + st.count('nachbesamen')}")
    mk = db.get_kosten_pro_monat(farm_id, monate=1)
    if mk and mk[-1]["gesamt"] > 0:
        lines.append(f"  Kosten diesen Monat: {mk[-1]['gesamt']:.0f} €")
    lines.append("\n💡 /besamung Emma · /brunft Emma · /tk Emma ja|nein")
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
        "<b>Abfragen:</b>\n/status — Termine: Stierigkeit, Untersuchung, Kalbung\n/tiere  — Alle Tiere auflisten\n/version — Auf neue Version prüfen\n/update  — HerdenPilot aktualisieren\n\n"
        "<b>Neues Tier anlegen:</b>\n/neues_tier Emma Rind     — Kuh namens Emma anlegen\n/neues_tier Wolke Schaf   — Schaf namens Wolke anlegen\n\n"
        "<b>Eingabe (aus dem Stall):</b>\n"
        "/besamung Emma            — Besamung heute\n/besamung Emma 85         — Besamung + 85 € Kosten\n"
        "/besamung Emma 24.05. 85  — Besamung mit Datum + Kosten\n/brunft Emma              — Brunft heute\n"
        "/geburt Emma              — Geburt heute\n/impfung Emma             — Impfung (läuft unter Tierarzt)\n"
        "/tierarzt Emma 150        — Tierarzt 150 €\n/kosten Emma 80           — Sonstige Kosten 80 €\n\n"
        "<b>Nach der Besamung:</b>\n"
        "Tag 21: auf Stierigkeit achten — stierig? → /brunft Emma, dann nachbesamen\n"
        "Tag 28: Trächtigkeitsuntersuchung → /tk Emma ja  oder  /tk Emma nein\n"
        "Die Termine stehen in /status und in der Morgenmeldung.\n\n"
        "<i>Namen können abgekürzt werden: /besamung em findet Emma</i>\n"
        "<i>Täglich zur eingestellten Uhrzeit: Termine von heute und den nächsten Tagen</i>"
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
    z, tk, tz = tier.get("brunft_zyklus"), tier.get("tk_tag"), tier.get("tragzeit")
    if z:
        antwort += f"\n👀 Auf Stierigkeit achten: <b>{(ereignis_datum + timedelta(days=z)).strftime('%d.%m.%Y')}</b> (Tag {z})"
    if tk:
        antwort += f"\n🔬 Trächtigkeitsuntersuchung: <b>{(ereignis_datum + timedelta(days=tk)).strftime('%d.%m.%Y')}</b> (Tag {tk})"
    if tz:
        antwort += f"\n🐣 Kalbung voraussichtlich: <b>{(ereignis_datum + timedelta(days=tz)).strftime('%d.%m.%Y')}</b>"
    return antwort


def cmd_ereignis(args: list, typ: str, farm_id: str, notiz: str = "") -> str:
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
    db.add_ereignis(farm_id, tier["id"], typ, ereignis_datum.isoformat(), notiz)
    dat_fmt = ereignis_datum.strftime("%d.%m.%Y")
    labels = {"besamung": "💉 Besamung", "brunft": "🌸 Brunft", "geburt": "🐣 Geburt", "tierarzt": "🩺 Tierarzt"}
    label = labels.get(typ, typ.capitalize()) + (f" ({notiz})" if notiz else "")
    antwort = f"✅ {label} für <b>{tier['name']}</b> eingetragen ({dat_fmt})."
    if typ == "brunft":
        a = fb.ablauf(tier, db.get_ereignisse_fuer_tier(tier["id"], farm_id), heute)
        if a["status"] == "nachbesamen":
            antwort += (f"\n🔴 Besamt am {a['besamung'].strftime('%d.%m.')} — wieder stierig: <b>nachbesamen!</b>"
                        f"\nDanach: /besamung {tier['name']}")
        elif tier.get("brunft_zyklus"):
            naechste = ereignis_datum + timedelta(days=tier["brunft_zyklus"])
            antwort += f"\n📅 Nächste Brunft ca.: {naechste.strftime('%d.%m.%Y')}"
    return antwort


_TK_JA = {"ja", "j", "+", "positiv", "pos", "trächtig", "traechtig"}
_TK_NEIN = {"nein", "n", "-", "negativ", "neg", "leer"}


def cmd_tk(args: list, farm_id: str) -> str:
    """Ergebnis der Trächtigkeitsuntersuchung: /tk Emma ja|nein [Datum vor dem Ergebnis]."""
    import database as db
    beispiel = "Beispiel: /tk Emma ja  oder  /tk Emma nein"
    if len(args) < 2:
        return f"❌ Bitte Tier und Ergebnis angeben.\n{beispiel}"
    teile = list(args)
    erg = teile.pop().lower()
    if erg in _TK_JA:
        typ = fb.TK_POS
    elif erg in _TK_NEIN:
        typ = fb.TK_NEG
    else:
        return f"❌ Ergebnis bitte mit <b>ja</b> oder <b>nein</b> angeben.\n{beispiel}"
    heute = date.today()
    datum = heute
    if len(teile) >= 2:
        d = datum_parsen(teile[-1])
        if d:
            datum = d
            teile.pop()
    tiere = db.get_alle_tiere(farm_id)
    suchname = " ".join(teile)
    tier, mehrere = find_tier(tiere, suchname)
    if mehrere:
        return f"❓ Mehrere Tiere gefunden: {', '.join(t['name'] for t in mehrere)}\nBitte genauer angeben."
    if not tier:
        return tier_nicht_gefunden(suchname, tiere)
    if tier.get("geschlecht") == "männlich":
        return f"❌ <b>{tier['name']}</b> ist männlich."
    db.add_ereignis(farm_id, tier["id"], typ, datum.isoformat())
    a = fb.ablauf(tier, db.get_ereignisse_fuer_tier(tier["id"], farm_id), heute)
    name = tier["name"]
    if typ == fb.TK_POS:
        r = f"✅ <b>{name}</b> ist trächtig (Untersuchung {datum.strftime('%d.%m.%Y')})."
        if a["kalbung"]:
            r += f"\n🐣 Kalbung voraussichtlich: <b>{a['kalbung'].strftime('%d.%m.%Y')}</b>"
        if not a["besamung"]:
            r += f"\n⚠️ Keine Besamung eingetragen — für den Kalbetermin: /besamung {name} TT.MM."
        return r
    r = f"❌ <b>{name}</b> ist nicht trächtig (Untersuchung {datum.strftime('%d.%m.%Y')})."
    brunft = [tm for tm in a["termine"] if tm["art"] == "brunft"]
    r += "\n👀 Auf Stierigkeit achten"
    if brunft:
        r += f", nächste Brunft ca. <b>{brunft[0]['datum'].strftime('%d.%m.%Y')}</b>"
    r += f"\nWenn stierig: /brunft {name}, dann /besamung {name}"
    return r


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


def _how_to_update() -> str:
    mode = updater.update_mode()
    if mode == "exe":
        return ("1. HerdenPilot schließen (das schwarze Fenster)\n"
                "2. <code>update.bat</code> doppelklicken\n"
                "3. Fertig — deine Daten bleiben alle erhalten")
    if mode == "auto":
        return "Einfach <b>/update</b> senden — der Rest läuft automatisch."
    return ("Per SSH auf dem Gerät:\n"
            "<code>cd ~/Tierkalb- && git pull && docker compose up -d --build</code>")


def build_version_message() -> str:
    if updater.update_mode() != "exe":
        code = updater.check_code_update()
        stand = f" (Stand {code['local']})" if code["local"] else ""
        if code["error"]:
            msg = f"ℹ️ HerdenPilot v{updater.APP_VERSION}{stand}\n{code['error']}"
            if updater.update_mode() == "auto":
                msg += "\n\nDen neuesten Stand holst du jederzeit mit /update."
            return msg
        if code["update_available"]:
            n = code["behind"]
            lines = [f"🔵 <b>{n} neue Änderung{'en' if n != 1 else ''} verfügbar</b>",
                     f"Stand {code['local']} → {code['remote']}"]
            for c in code["changes"]:
                lines.append(f"  • {_html.escape(c)}")
            lines.append("")
            lines.append("<b>So aktualisierst du:</b>")
            lines.append(_how_to_update())
            return "\n".join(lines)
        return f"✅ HerdenPilot v{updater.APP_VERSION}{stand} — du bist auf dem neuesten Stand."

    info = updater.check_for_update()
    if info["error"]:
        msg = f"⚠️ Update-Prüfung nicht möglich:\n{info['error']}"
        if updater.update_mode() == "auto":
            msg += "\n\nDen neuesten Stand holst du trotzdem jederzeit mit /update."
        return msg
    if info["update_available"]:
        return (
            f"🔵 <b>Neue Version verfügbar: {info['latest']}</b>\n"
            f"Deine Version: v{info['current']}\n\n"
            "<b>So aktualisierst du:</b>\n"
            f"{_how_to_update()}\n\n"
            f"Details: {info['release_page']}"
        )
    return f"✅ HerdenPilot v{info['current']} — du bist auf dem neuesten Stand."


def cmd_update() -> str:
    mode = updater.update_mode()
    if mode == "exe":
        return ("💻 Das ist die Windows-Version.\n"
                "Update: HerdenPilot schließen → <code>update.bat</code> doppelklicken.")
    if mode == "manual":
        return ("🛠 Automatisches Update ist auf diesem Gerät nicht eingerichtet.\n\n"
                "Per SSH:\n<code>cd ~/Tierkalb- && git pull && docker compose up -d --build</code>\n\n"
                "Einmalig einrichten (danach geht /update):\n"
                "<code>sudo bash autoupdate/install-updater.sh</code>")
    if updater.update_running():
        return "⏳ Es läuft bereits ein Update — ich melde mich, sobald es fertig ist."
    updater.request_update("telegram")
    return ("🔄 <b>Update gestartet.</b>\n"
            "Dauert 2–5 Minuten, HerdenPilot ist dabei kurz nicht erreichbar.\n"
            "Ich melde mich, sobald es fertig ist. Deine Daten bleiben erhalten.")


def check_update_result(app):
    try:
        res = updater.pop_update_result()
    except Exception as e:
        print(f"[Update] Ergebnis lesen fehlgeschlagen: {e}")
        return
    if not res:
        return
    if res["status"] == "done":
        if res["old"] == res["new"]:
            text = f"✅ <b>Update geprüft</b> — HerdenPilot war bereits aktuell (Stand {res['new']})."
        else:
            text = (f"✅ <b>Update abgeschlossen!</b>\n"
                    f"Stand: {res['old']} → {res['new']}\n"
                    "Alle Daten sind erhalten.")
    else:
        text = ("❌ <b>Update fehlgeschlagen</b> — die bisherige Version läuft unverändert weiter.\n\n"
                f"<code>{_html.escape(res.get('log', '')[-800:])}</code>")
    with app.app_context():
        import database as db
        for farm in db.get_all_farms():
            fid = farm["id"]
            token   = db.get_config(fid, "telegram_token", "")
            chat_id = db.get_config(fid, "telegram_chat_id", "")
            if token and chat_id:
                send_message(token, chat_id, text)
            ntfy_topic = db.get_config(fid, "ntfy_topic", "")
            if ntfy_topic and db.get_config(fid, "notify_ntfy", "0") == "1":
                send_ntfy(ntfy_topic, text, db.get_config(fid, "ntfy_server", "ntfy.sh"))


def handle_command(text: str, farm_id: str, farm_name: str):
    import database as db
    parts = text.strip().split()
    if not parts: return None
    cmd = parts[0].lower().split("@")[0]; args = parts[1:]
    if cmd == "/status":     return build_status_message(farm_id, farm_name)
    elif cmd == "/tiere":    return build_tiere_message(db.get_alle_tiere(farm_id), farm_name)
    elif cmd in ("/hilfe", "/help", "/start"): return build_hilfe_message(farm_name)
    elif cmd == "/version":    return build_version_message()
    elif cmd == "/update":     return cmd_update()
    elif cmd == "/neues_tier": return cmd_neues_tier(args, farm_id)
    elif cmd == "/besamung":   return cmd_besamung(args, farm_id)
    elif cmd == "/brunft":     return cmd_ereignis(args, "brunft", farm_id)
    elif cmd == "/geburt":     return cmd_ereignis(args, "geburt", farm_id)
    elif cmd == "/impfung":    return cmd_ereignis(args, "tierarzt", farm_id, notiz="Impfung")
    elif cmd == "/tk":         return cmd_tk(args, farm_id)
    elif cmd == "/tierarzt":   return cmd_kosten(args, "Tierarzt", farm_id)
    elif cmd == "/kosten":     return cmd_kosten(args, "Sonstiges", farm_id)
    return None


def _berlin_now_hm() -> str:
    from datetime import datetime
    try:
        import pytz
        return datetime.now(pytz.timezone("Europe/Berlin")).strftime("%H:%M")
    except Exception:
        return datetime.now().strftime("%H:%M")


def send_daily_update(app):
    now_hm = _berlin_now_hm()
    with app.app_context():
        import database as db
        for farm in db.get_all_farms():
            fid = farm["id"]
            if (db.get_config(fid, "notify_time", "06:00") or "06:00") != now_hm:
                continue
            heute = date.today()
            _, _, termin_zeilen = _termin_bloecke(fid, heute, ["ueberfaellig", "heute", "woche"])
            if not termin_zeilen:
                continue
            lines = [f"<b>🌅 Guten Morgen! — {farm['name']}</b>", ""] + termin_zeilen
            lines.append("💡 /status für alle Termine")
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
        scheduler.add_job(send_daily_update, "cron", minute="*", args=[app], id="daily_update", replace_existing=True)
        scheduler.add_job(check_update_result, "interval", seconds=30, args=[app], id="update_result", replace_existing=True)
        scheduler.start()
        print("[Telegram] Scheduler gestartet (Meldezeit je Betrieb einstellbar, Europe/Berlin)")
        t = threading.Thread(target=polling_worker, args=(app,), daemon=True)
        t.start()
        print("[Telegram] Polling-Thread gestartet")
        return scheduler
    except Exception as e:
        print(f"[Telegram] Start-Fehler: {e}")
        return None
