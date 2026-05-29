"""
database.py — SQLite für Tierkalb v3.0
"""

import sqlite3
import os
from datetime import date, datetime, timedelta
import uuid

DATABASE_PATH = os.environ.get("DATABASE_PATH", "./data/tierkalb.db")


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH) or ".", exist_ok=True)
    conn = get_connection()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS farms (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            owner_name  TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            timezone    TEXT DEFAULT 'Europe/Berlin'
        );

        CREATE TABLE IF NOT EXISTS config (
            farm_id TEXT NOT NULL,
            key     TEXT NOT NULL,
            value   TEXT,
            PRIMARY KEY (farm_id, key),
            FOREIGN KEY (farm_id) REFERENCES farms(id)
        );

        CREATE TABLE IF NOT EXISTS tierarten (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            farm_id        TEXT NOT NULL,
            name           TEXT NOT NULL,
            brunft_zyklus  INTEGER,
            tragzeit       INTEGER,
            emoji          TEXT,
            FOREIGN KEY (farm_id) REFERENCES farms(id),
            UNIQUE(farm_id, name)
        );

        CREATE TABLE IF NOT EXISTS tiere (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            farm_id      TEXT NOT NULL,
            name         TEXT NOT NULL,
            ohrmarke     TEXT,
            tierart_id   INTEGER,
            geburtsdatum DATE,
            geschlecht   TEXT DEFAULT 'weiblich',
            status       TEXT DEFAULT 'Aktiv',
            notiz        TEXT,
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (farm_id) REFERENCES farms(id),
            FOREIGN KEY (tierart_id) REFERENCES tierarten(id)
        );

        CREATE TABLE IF NOT EXISTS ereignisse (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            tier_id    INTEGER NOT NULL,
            farm_id    TEXT NOT NULL,
            typ        TEXT NOT NULL,
            datum      DATE NOT NULL,
            notiz      TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tier_id) REFERENCES tiere(id),
            FOREIGN KEY (farm_id) REFERENCES farms(id)
        );

        CREATE TABLE IF NOT EXISTS kosten (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            tier_id    INTEGER NOT NULL,
            farm_id    TEXT NOT NULL,
            typ        TEXT NOT NULL,
            betrag     REAL NOT NULL,
            datum      DATE NOT NULL,
            notiz      TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tier_id) REFERENCES tiere(id),
            FOREIGN KEY (farm_id) REFERENCES farms(id)
        );
    """)
    # Migrations: Spalten hinzufügen falls sie noch nicht existieren (für alte DBs)
    for col, definition in [("geschlecht", "TEXT DEFAULT 'weiblich'"), ("notiz", "TEXT")]:
        try:
            conn.execute(f"ALTER TABLE tiere ADD COLUMN {col} {definition}")
        except Exception:
            pass
    conn.commit()
    conn.close()


# ─── Farms ───────────────────────────────────────────────────────────────

def create_farm(farm_name: str, owner_name: str = None) -> str:
    farm_id = str(uuid.uuid4())[:12]
    conn = get_connection()
    conn.execute(
        "INSERT INTO farms (id, name, owner_name) VALUES (?, ?, ?)",
        (farm_id, farm_name, owner_name)
    )
    conn.commit()
    conn.close()
    return farm_id


def get_farm(farm_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM farms WHERE id = ?", (farm_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_farms() -> list:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM farms").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Config ───────────────────────────────────────────────────────────────

def set_config(farm_id: str, key: str, value: str):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO config (farm_id, key, value) VALUES (?, ?, ?)",
        (farm_id, key, value)
    )
    conn.commit()
    conn.close()


def get_config(farm_id: str, key: str, default=None):
    conn = get_connection()
    row = conn.execute(
        "SELECT value FROM config WHERE farm_id = ? AND key = ?",
        (farm_id, key)
    ).fetchone()
    conn.close()
    return row["value"] if row else default


# ─── Tierarten ────────────────────────────────────────────────────────────

def upsert_tierart(farm_id: str, name: str, brunft: int, tragzeit: int, emoji: str):
    conn = get_connection()
    conn.execute("""
        INSERT INTO tierarten (farm_id, name, brunft_zyklus, tragzeit, emoji)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(farm_id, name) DO UPDATE SET
            brunft_zyklus = excluded.brunft_zyklus,
            tragzeit = excluded.tragzeit,
            emoji = excluded.emoji
    """, (farm_id, name, brunft, tragzeit, emoji))
    conn.commit()
    conn.close()


def get_tierarten(farm_id: str) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tierarten WHERE farm_id = ? ORDER BY name",
        (farm_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Tiere ────────────────────────────────────────────────────────────────

def add_tier(farm_id, name, ohrmarke, tierart_id, geburtsdatum=None,
             geschlecht="weiblich", notiz="") -> int:
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO tiere (farm_id, name, ohrmarke, tierart_id,
           geburtsdatum, geschlecht, notiz) VALUES (?,?,?,?,?,?,?)""",
        (farm_id, name, ohrmarke or None, tierart_id,
         geburtsdatum or None, geschlecht, notiz or None)
    )
    tier_id = cur.lastrowid
    conn.commit()
    conn.close()
    return tier_id


def edit_tier(tier_id, farm_id, name, ohrmarke, tierart_id,
              geburtsdatum, status, geschlecht, notiz):
    conn = get_connection()
    conn.execute("""
        UPDATE tiere SET name=?, ohrmarke=?, tierart_id=?,
        geburtsdatum=?, status=?, geschlecht=?, notiz=?
        WHERE id=? AND farm_id=?
    """, (name, ohrmarke or None, tierart_id,
          geburtsdatum or None, status, geschlecht,
          notiz or None, tier_id, farm_id))
    conn.commit()
    conn.close()


def archiviere_tier(tier_id: int, farm_id: str):
    conn = get_connection()
    conn.execute(
        "UPDATE tiere SET status='Archiviert' WHERE id=? AND farm_id=?",
        (tier_id, farm_id)
    )
    conn.commit()
    conn.close()


def get_tier_count(farm_id: str) -> int:
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM tiere WHERE farm_id=? AND status='Aktiv'",
        (farm_id,)
    ).fetchone()[0]
    conn.close()
    return count


def get_alle_tiere(farm_id: str, nur_aktiv=True) -> list:
    conn = get_connection()
    where = "AND t.status='Aktiv'" if nur_aktiv else ""
    rows = conn.execute(f"""
        SELECT t.*, ta.name AS tierart_name,
               ta.brunft_zyklus, ta.tragzeit, ta.emoji
        FROM tiere t
        LEFT JOIN tierarten ta ON t.tierart_id = ta.id
        WHERE t.farm_id=? {where}
        ORDER BY t.name
    """, (farm_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_tier_by_id(tier_id: int, farm_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("""
        SELECT t.*, ta.name AS tierart_name,
               ta.brunft_zyklus, ta.tragzeit, ta.emoji
        FROM tiere t
        LEFT JOIN tierarten ta ON t.tierart_id = ta.id
        WHERE t.id=? AND t.farm_id=?
    """, (tier_id, farm_id)).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Ereignisse ───────────────────────────────────────────────────────────

def add_ereignis(farm_id, tier_id, typ, datum, notiz=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO ereignisse (farm_id, tier_id, typ, datum, notiz) VALUES (?,?,?,?,?)",
        (farm_id, tier_id, typ, datum, notiz or None)
    )
    conn.commit()
    conn.close()


def delete_ereignis(ereignis_id: int, farm_id: str):
    conn = get_connection()
    conn.execute(
        "DELETE FROM ereignisse WHERE id=? AND farm_id=?",
        (ereignis_id, farm_id)
    )
    conn.commit()
    conn.close()


def get_ereignisse_fuer_tier(tier_id: int, farm_id: str) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM ereignisse WHERE tier_id=? AND farm_id=? ORDER BY datum DESC",
        (tier_id, farm_id)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_letztes_ereignis(tier_id: int, farm_id: str, typ: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("""
        SELECT * FROM ereignisse
        WHERE tier_id=? AND farm_id=? AND typ=?
        ORDER BY datum DESC LIMIT 1
    """, (tier_id, farm_id, typ)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_upcoming_geburten(farm_id: str, days: int = 30) -> list:
    """Tiere mit erwarteter Geburt in den nächsten N Tagen"""
    today = date.today().isoformat()
    future = (date.today() + timedelta(days=days)).isoformat()
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            t.id, t.name,
            ta.tragzeit, ta.emoji,
            e.datum AS letzte_besamung,
            date(e.datum, '+' || CAST(ta.tragzeit AS TEXT) || ' days') AS erwartete_geburt
        FROM tiere t
        JOIN tierarten ta ON t.tierart_id = ta.id
        JOIN ereignisse e ON e.tier_id = t.id
            AND e.farm_id = t.farm_id AND e.typ = 'besamung'
        WHERE t.farm_id = ?
          AND t.status = 'Aktiv'
          AND e.id = (
              SELECT e2.id FROM ereignisse e2
              WHERE e2.tier_id = t.id AND e2.farm_id = t.farm_id AND e2.typ = 'besamung'
              ORDER BY e2.datum DESC LIMIT 1
          )
          AND date(e.datum, '+' || CAST(ta.tragzeit AS TEXT) || ' days') BETWEEN ? AND ?
        ORDER BY erwartete_geburt
    """, (farm_id, today, future)).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        if d["erwartete_geburt"]:
            try:
                eb = date.fromisoformat(d["erwartete_geburt"])
                d["erwartete_geburt_fmt"] = eb.strftime("%d.%m.%Y")
                d["tage_bis_geburt"] = (eb - date.today()).days
            except Exception:
                d["erwartete_geburt_fmt"] = d["erwartete_geburt"]
                d["tage_bis_geburt"] = 0
        result.append(d)
    return result


# ─── Kosten ───────────────────────────────────────────────────────────────

def add_kosten(farm_id, tier_id, typ, betrag, datum, notiz=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO kosten (farm_id, tier_id, typ, betrag, datum, notiz) VALUES (?,?,?,?,?,?)",
        (farm_id, tier_id, typ, betrag, datum, notiz or None)
    )
    conn.commit()
    conn.close()


def delete_kosten(kosten_id: int, farm_id: str):
    conn = get_connection()
    conn.execute(
        "DELETE FROM kosten WHERE id=? AND farm_id=?",
        (kosten_id, farm_id)
    )
    conn.commit()
    conn.close()


def get_kosten_fuer_tier(tier_id: int, farm_id: str) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM kosten WHERE tier_id=? AND farm_id=? ORDER BY datum DESC",
        (tier_id, farm_id)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_gesamtkosten(farm_id: str) -> float:
    conn = get_connection()
    val = conn.execute(
        "SELECT COALESCE(SUM(betrag), 0) FROM kosten WHERE farm_id=?",
        (farm_id,)
    ).fetchone()[0]
    conn.close()
    return float(val)


def get_kosten_pro_tier(farm_id: str) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT t.id, t.name, COALESCE(SUM(k.betrag), 0) AS gesamt
        FROM tiere t
        LEFT JOIN kosten k ON k.tier_id = t.id AND k.farm_id = t.farm_id
        WHERE t.farm_id = ? AND t.status = 'Aktiv'
        GROUP BY t.id ORDER BY gesamt DESC
    """, (farm_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_kosten_pro_typ(farm_id: str) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT typ, COALESCE(SUM(betrag), 0) AS gesamt
        FROM kosten WHERE farm_id=?
        GROUP BY typ ORDER BY gesamt DESC
    """, (farm_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_kosten_pro_monat(farm_id: str, monate: int = 12) -> list:
    """Kosten der letzten N Monate, alle Monate gefüllt (auch 0)"""
    conn = get_connection()
    rows = conn.execute("""
        SELECT strftime('%Y-%m', datum) AS monat,
               COALESCE(SUM(betrag), 0) AS gesamt
        FROM kosten
        WHERE farm_id = ?
          AND datum >= date('now', '-' || ? || ' months')
        GROUP BY strftime('%Y-%m', datum)
        ORDER BY monat
    """, (farm_id, monate)).fetchall()
    conn.close()
    db_data = {r["monat"]: round(float(r["gesamt"]), 2) for r in rows}
    # Alle Monate auffüllen (auch ohne Kosten = 0)
    result = []
    for i in range(monate - 1, -1, -1):
        m = (date.today().replace(day=1) - timedelta(days=i * 28))
        key = m.strftime("%Y-%m")
        label = m.strftime("%b %Y")
        result.append({"monat": key, "label": label, "gesamt": db_data.get(key, 0.0)})
    return result


def get_besamungs_statistik(farm_id: str) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            t.name AS tier_name,
            t.id   AS tier_id,
            SUM(CASE WHEN e.typ='besamung' THEN 1 ELSE 0 END) AS besamungen,
            SUM(CASE WHEN e.typ='geburt'   THEN 1 ELSE 0 END) AS geburten
        FROM tiere t
        LEFT JOIN ereignisse e ON e.tier_id=t.id AND e.farm_id=t.farm_id
        WHERE t.farm_id=? AND t.status='Aktiv'
        GROUP BY t.id
        HAVING besamungen > 0 OR geburten > 0
        ORDER BY t.name
    """, (farm_id,)).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        b = d["besamungen"] or 0
        g = d["geburten"] or 0
        d["erfolgsrate"] = round(g / b * 100) if b > 0 else 0
        result.append(d)
    return result
