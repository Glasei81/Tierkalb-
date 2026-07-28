"""
updater.py — Prüft, ob eine neuere HerdenPilot-Version auf GitHub verfügbar ist.
"""

import requests

APP_VERSION = "1.0"
REPO = "Glasei81/Tierkalb-"
RELEASE_PAGE = f"https://github.com/{REPO}/releases/latest"
EXE_DOWNLOAD = f"https://github.com/{REPO}/releases/latest/download/HerdenPilot.exe"


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
