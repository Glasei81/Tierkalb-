"""
telegram_bot.py — Tägliche Benachrichtigungen via Telegram
APScheduler sendet täglich um 6:00 Uhr anstehende Geburten.
"""

import requests
from datetime import date


def send_message(token: str, chat_id: str, text: str) -> bool:
    """Telegram-Nachricht senden via Bot API"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(
            url,
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
        return r.ok
    except Exception as e:
        print(f"[Telegram] Fehler beim Senden: {e}")
        return False


def send_daily_update(app):
    """Wird täglich um 6:00 Uhr aufgerufen"""
    with app.app_context():
        import database as db

        farms = db.get_all_farms()
        for farm in farms:
            fid = farm["id"]
            token = db.get_config(fid, "telegram_token", "")
            chat_id = db.get_config(fid, "telegram_chat_id", "")
            if not token or not chat_id:
                continue

            upcoming = db.get_upcoming_geburten(fid, days=14)
            if not upcoming:
                continue

            lines = [f"<b>Tierkalb — {farm['name']}</b>"]
            lines.append(f"Anstehende Geburten (nächste 14 Tage):\n")

            for u in upcoming:
                tage = u.get("tage_bis_geburt", 0)
                name = u["name"]
                datum = u.get("erwartete_geburt_fmt", "")
                emoji = u.get("emoji", "🐄")

                if tage == 0:
                    lines.append(f"🔴 {emoji} <b>{name}</b> — <b>heute erwartet!</b>")
                elif tage == 1:
                    lines.append(f"🟠 {emoji} <b>{name}</b> — morgen ({datum})")
                elif tage <= 3:
                    lines.append(f"🟡 {emoji} {name} — in {tage} Tagen ({datum})")
                else:
                    lines.append(f"🟢 {emoji} {name} — in {tage} Tagen ({datum})")

            send_message(token, chat_id, "\n".join(lines))


def start_scheduler(app):
    """APScheduler starten — täglich 6:00 Uhr Lokalzeit"""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler

        scheduler = BackgroundScheduler()
        scheduler.add_job(
            send_daily_update,
            "cron",
            hour=6,
            minute=0,
            args=[app],
            id="daily_update",
            replace_existing=True,
        )
        scheduler.start()
        print("[Telegram] Scheduler gestartet (täglich 6:00 Uhr)")
        return scheduler
    except Exception as e:
        print(f"[Telegram] Scheduler konnte nicht gestartet werden: {e}")
        return None
