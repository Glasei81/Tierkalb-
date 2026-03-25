"""
database.py — SQLite für Tierkalb v2.0
Multi-Farm Support mit Lizenz-System
"""

import sqlite3
import os
from datetime import date, datetime, timedelta
import uuid

DATABASE_PATH = os.environ.get("DATABASE_PATH", "./data/tierkalb.db")


def get_connection():
    """DB-Verbindung mit Foreign Keys"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Datenbank initialisieren"""
    os.makedirs(os.path.dirname(DATABASE_PATH) or ".", exist_ok=True)
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
        -- Farms (Multi-Tenant)
        CREATE TABLE IF NOT EXISTS farms (
            id                TEXT PRIMARY KEY,
            name              TEXT NOT NULL,
            owner_name        TEXT,
            created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
            timezone          TEXT DEFAULT 'Europe/Berlin'
        );

        -- Lizenzen (Pro-Version)
        CREATE TABLE IF NOT EXISTS licenses (
            id                TEXT PRIMARY KEY,
            farm_id           TEXT NOT NULL UNIQUE,
            is_pro            BOOLEAN DEFAULT 0,
            license_key       TEXT,
            purchased_at      DATETIME,
            expires_at        DATETIME,
            FOREIGN KEY (farm_id) REFERENCES farms(id)
        );

        -- Konfiguration pro Farm
        CREATE TABLE IF NOT EXISTS config (
            farm_id           TEXT NOT NULL,
            key               TEXT NOT NULL,
            value             TEXT,
            PRIMARY KEY (farm_id, key),
            FOREIGN KEY (farm_id) REFERENCES farms(id)
        );

        -- Tierarten
        CREATE TABLE IF NOT EXISTS tierarten (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            farm_id           TEXT NOT NULL,
            name              TEXT NOT NULL,
            brunft_zyklus     INTEGER,
            tragzeit          INTEGER,
            emoji             TEXT,
            FOREIGN KEY (farm_id) REFERENCES farms(id),
            UNIQUE(farm_id, name)
        );

        -- Tiere
        CREATE TABLE IF NOT EXISTS tiere (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            farm_id           TEXT NOT NULL,
            name              TEXT NOT NULL,
            ohrmarke          TEXT,
            tierart_id        INTEGER,
            geburtsdatum      DATE,
            status            TEXT DEFAULT 'Aktiv',
            created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (farm_id) REFERENCES farms(id),
            FOREIGN KEY (tierart_id) REFERENCES tierarten(id)
        );

        -- Ereignisse (Brunft, Besamung, Geburt, etc.)
        CREATE TABLE IF NOT EXISTS ereignisse (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            tier_id           INTEGER NOT NULL,
            farm_id           TEXT NOT NULL,
            typ               TEXT NOT NULL,
            datum             DATE NOT NULL,
            notiz             TEXT,
            created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tier_id) REFERENCES tiere(id),
            FOREIGN KEY (farm_id) REFERENCES farms(id)
        );

        -- Kosten
        CREATE TABLE IF NOT EXISTS kosten (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            tier_id           INTEGER NOT NULL,
            farm_id           TEXT NOT NULL,
            typ               TEXT NOT NULL,
            betrag            REAL NOT NULL,
            datum             DATE NOT NULL,
            notiz             TEXT,
            created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tier_id) REFERENCES tiere(id),
            FOREIGN KEY (farm_id) REFERENCES farms(id)
        );
    """)

    conn.commit()
    conn.close()


# ─── Farm-Management ──────────────────────────────────────────────────────

def create_farm(farm_name: str, owner_name: str = None) -> str:
    """Neue Farm erstellen, gibt Farm-ID zurück"""
    farm_id = str(uuid.uuid4())[:12]
    conn = get_connection()
    conn.execute(
        "INSERT INTO farms (id, name, owner_name) VALUES (?, ?, ?)",
        (farm_id, farm_name, owner_name)
    )
    # Lizenz hinzufügen (kostenlos)
    conn.execute(
        "INSERT INTO licenses (id, farm_id, is_pro) VALUES (?, ?, 0)",
        (str(uuid.uuid4()), farm_id)
    )
    conn.commit()
    conn.close()
    return farm_id


def get_farm(farm_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM farms WHERE id = ?", (farm_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Lizenz-Management ────────────────────────────────────────────────────

def get_license(farm_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM licenses WHERE farm_id = ?", (farm_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def is_pro(farm_id: str) -> bool:
    """Prüfe ob Farm Pro-Version hat"""
    lic = get_license(farm_id)
    if not lic:
        return False
    return lic.get("is_pro", False) == 1


def unlock_pro(farm_id: str, license_key: str) -> bool:
    """Pro-Version freischalten mit Lizenz-Key"""
    conn = get_connection()
    conn.execute(
        "UPDATE licenses SET is_pro = 1, license_key = ?, purchased_at = ? WHERE farm_id = ?",
        (license_key, datetime.now().isoformat(), farm_id)
    )
    conn.commit()
    conn.close()
    return True


# ─── Konfiguration ────────────────────────────────────────────────────────

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

def get_tier_count(farm_id: str) -> int:
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM tiere WHERE farm_id = ? AND status = 'Aktiv'",
        (farm_id,)
    ).fetchone()[0]
    conn.close()
    return count


def add_tier(farm_id: str, name: str, ohrmarke: str, tierart_id: int, geburtsdatum=None) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO tiere (farm_id, name, ohrmarke, tierart_id, geburtsdatum) VALUES (?, ?, ?, ?, ?)",
        (farm_id, name, ohrmarke or None, tierart_id, geburtsdatum or None)
    )
    tier_id = cur.lastrowid
    conn.commit()
    conn.close()
    return tier_id


def get_alle_tiere(farm_id: str) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT t.*, ta.name AS tierart_name, ta.brunft_zyklus, ta.tragzeit, ta.emoji
        FROM tiere t
        LEFT JOIN tierarten ta ON t.tierart_id = ta.id
        WHERE t.farm_id = ?
        ORDER BY t.name
    """, (farm_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_tier_by_id(tier_id: int, farm_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("""
        SELECT t.*, ta.name AS tierart_name, ta.brunft_zyklus, ta.tragzeit, ta.emoji
        FROM tiere t
        LEFT JOIN tierarten ta ON t.tierart_id = ta.id
        WHERE t.id = ? AND t.farm_id = ?
    """, (tier_id, farm_id)).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Ereignisse ───────────────────────────────────────────────────────────

def add_ereignis(farm_id: str, tier_id: int, typ: str, datum: str, notiz: str = ""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO ereignisse (farm_id, tier_id, typ, datum, notiz) VALUES (?, ?, ?, ?, ?)",
        (farm_id, tier_id, typ, datum, notiz or None)
    )
    conn.commit()
    conn.close()


def get_ereignisse_fuer_tier(tier_id: int, farm_id: str) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM ereignisse WHERE tier_id = ? AND farm_id = ? ORDER BY datum DESC",
        (tier_id, farm_id)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_letztes_ereignis(tier_id: int, farm_id: str, typ: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("""
        SELECT * FROM ereignisse
        WHERE tier_id = ? AND farm_id = ? AND typ = ?
        ORDER BY datum DESC LIMIT 1
    """, (tier_id, farm_id, typ)).fetchone()
    conn.close()
    return dict(row) if row else None


# ─── Kosten ───────────────────────────────────────────────────────────────

def add_kosten(farm_id: str, tier_id: int, typ: str, betrag: float, datum: str, notiz: str = ""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO kosten (farm_id, tier_id, typ, betrag, datum, notiz) VALUES (?, ?, ?, ?, ?, ?)",
        (farm_id, tier_id, typ, betrag, datum, notiz or None)
    )
    conn.commit()
    conn.close()


def get_kosten_fuer_tier(tier_id: int, farm_id: str) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM kosten WHERE tier_id = ? AND farm_id = ? ORDER BY datum DESC",
        (tier_id, farm_id)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_kosten_statistik(farm_id: str) -> dict:
    """Kosten-Übersicht pro Tier und gesamt"""
    conn = get_connection()
    rows = conn.execute("""
        SELECT t.id, t.name, SUM(k.betrag) as gesamt
        FROM tiere t
        LEFT JOIN kosten k ON t.id = k.tier_id AND t.farm_id = k.farm_id
        WHERE t.farm_id = ?
        GROUP BY t.id
        ORDER BY gesamt DESC
    """, (farm_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Statistik (PRO) ──────────────────────────────────────────────────────

def get_besamungs_statistik(farm_id: str) -> dict:
    """Besamungs-Erfolgsrate"""
    conn = get_connection()
    
    # Anzahl Besamungen pro Tier
    besamungen = conn.execute("""
        SELECT COUNT(*) as count, tier_id
        FROM ereignisse
        WHERE farm_id = ? AND typ = 'besamung'
        GROUP BY tier_id
    """, (farm_id,)).fetchall()
    
    # Anzahl Geburten pro Tier
    geburten = conn.execute("""
        SELECT COUNT(*) as count, tier_id
        FROM ereignisse
        WHERE farm_id = ? AND typ = 'geburt'
        GROUP BY tier_id
    """, (farm_id,)).fetchall()
    
    conn.close()
    
    return {
        "besamungen": [dict(r) for r in besamungen],
        "geburten": [dict(r) for r in geburten],
    }
