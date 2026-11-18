"""
updater.py — Versionsprüfung (GitHub) und Steuerung des automatischen Updates.
"""

import os
import sys
import time
from datetime import datetime

import requests

APP_VERSION = "1.0"
REPO = "Glasei81/Tierkalb-"
RELEASE_PAGE = f"https://github.com/{REPO}/releases/latest"
EXE_DOWNLOAD = f"https://github.com/{REPO}/releases/latest/download/HerdenPilot.exe"

_STALE_SECONDS = 30 * 60


def _parse(v: str):
    v = (v or "").strip().lstrip("vV")
    parts = []
    for p in v.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts) or (0,)


def check_for_update(timeout: int = 8) -> dict:
    result = {
        "current": APP_VERSION,
        "latest": None,
        "update_available": False,
        "release_page": RELEASE_PAGE,
        "download_url": EXE_DOWNLOAD,
        "error": None,
    }
    try:
        r = requests.get(
            f"https://api.github.com/repos/{REPO}/releases/latest",
            headers={"Accept": "application/vnd.github+json"},
            timeout=timeout,
        )
        if r.status_code == 404:
            result["error"] = "Noch keine Version auf GitHub veröffentlicht."
            return result
        if not r.ok:
            result["error"] = f"GitHub nicht erreichbar (Code {r.status_code})."
            return result
        tag = (r.json().get("tag_name") or "").strip()
        if not tag:
            result["error"] = "Keine Versionsinformation gefunden."
            return result
        result["latest"] = tag
        result["update_available"] = _parse(tag) > _parse(APP_VERSION)
    except Exception:
        result["error"] = "Keine Internetverbindung — Prüfung nicht möglich."
    return result


def update_mode() -> str:
    """exe = Windows-exe, auto = Pi/Server mit eingerichtetem Auto-Update, manual = Server ohne."""
    if getattr(sys, "frozen", False):
        return "exe"
    if os.environ.get("AUTO_UPDATE", "").strip() == "1":
        return "auto"
    return "manual"


def _data_dir() -> str:
    import database as db
    return os.path.dirname(os.path.abspath(db.DATABASE_PATH))


def _fresh(path: str) -> bool:
    try:
        return (time.time() - os.path.getmtime(path)) < _STALE_SECONDS
    except OSError:
        return False


def update_running() -> bool:
    d = _data_dir()
    return any(_fresh(os.path.join(d, n)) for n in ("update.request", "update.running"))


def request_update(source: str = "") -> None:
    d = _data_dir()
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "update.request"), "w", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat(timespec='seconds')} {source}\n")


def pop_update_result():
    d = _data_dir()
    done = os.path.join(d, "update.done")
    failed = os.path.join(d, "update.failed")
    if os.path.exists(done):
        try:
            parts = open(done, encoding="utf-8").read().split()
        except OSError:
            parts = []
        os.remove(done)
        return {"status": "done",
                "old": parts[0] if parts else "?",
                "new": parts[1] if len(parts) > 1 else "?"}
    if os.path.exists(failed):
        try:
            log = open(failed, encoding="utf-8", errors="replace").read()
        except OSError:
            log = ""
        os.remove(failed)
        return {"status": "failed", "log": log[-1500:]}
    return None
