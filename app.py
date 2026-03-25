"""
app.py — Tierkalb v2.0
Multi-Farm, Pro-Lizenz, Statistik, Export
"""

import os
from datetime import date, timedelta
from functools import wraps
import csv
from io import StringIO

from flask import (
    Flask, render_template, request, redirect, url_for, 
    session, jsonify, flash, send_file
)

import database as db
from tierarten import TIERARTEN, I18N, MAX_TIERE_FREE, PRO_PRICE

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "tierkalb-v2-secret")


# ─── Middleware ──────────────────────────────────────────────────────────

def get_farm_id():
    """Farm-ID aus Session oder Query-Param"""
    if "farm_id" in session:
        return session["farm_id"]
    farm_id = request.args.get("farm_id") or request.form.get("farm_id")
    if farm_id:
        session["farm_id"] = farm_id
    return farm_id


def require_farm(f):
    """Decorator: Farm muss gesetzt sein"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        farm_id = get_farm_id()
        if not farm_id or not db.get_farm(farm_id):
            return redirect(url_for("setup"))
        return f(*args, **kwargs)
    return decorated_function


def require_pro(f):
    """Decorator: Pro-Version erforderlich"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        farm_id = get_farm_id()
        if not farm_id or not db.is_pro(farm_id):
            flash("Pro-Version erforderlich", "warning")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated_function


def get_lang():
    """Sprache aus Config oder Standard"""
    farm_id = get_farm_id()
    if farm_id:
        return db.get_config(farm_id, "lang", "de")
    return "de"


def t(key: str) -> str:
    """Translate key"""
    lang = get_lang()
    return I18N.get(lang, I18N["de"]).get(key, key)


# ─── Routen ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    farm_id = get_farm_id()
    if farm_id and db.get_farm(farm_id):
        return redirect(url_for("dashboard", farm_id=farm_id))
    return redirect(url_for("setup"))


@app.route("/setup", methods=["GET", "POST"])
def setup():
    """Farm-Setup (ersetzt Wizard aus v1)"""
    if request.method == "POST":
        farm_name = request.form.get("farm_name", "").strip()
        owner_name = request.form.get("owner_name", "").strip()
        
        if not farm_name:
            flash("Bitte Betriebsnamen eingeben", "error")
            return render_template("setup.html", t=t)
        
        farm_id = db.create_farm(farm_name, owner_name)
        session["farm_id"] = farm_id
        
        # Alle Tierarten hinzufügen
        for name, cfg in TIERARTEN.items():
            db.upsert_tierart(farm_id, name, cfg["brunft"], cfg["tragzeit"], cfg["emoji"])
        
        db.set_config(farm_id, "lang", request.form.get("lang", "de"))
        
        flash("✅ Farm erstellt! Willkommen!", "success")
        return redirect(url_for("dashboard", farm_id=farm_id))
    
    return render_template("setup.html", t=t, TIERARTEN=TIERARTEN)


@app.route("/dashboard")
@require_farm
def dashboard():
    farm_id = get_farm_id()
    farm = db.get_farm(farm_id)
    license = db.get_license(farm_id)
    tiere = db.get_alle_tiere(farm_id)
    tier_count = db.get_tier_count(farm_id)
    
    # Statistiken für Tiere
    tiere_mit_info = []
    for tier in tiere:
        info = dict(tier)
        letztes = db.get_letztes_ereignis(tier["id"], farm_id, "brunft") or \
                  db.get_letztes_ereignis(tier["id"], farm_id, "besamung")
        info["letztes_ereignis"] = letztes
        
        # Nächste Brunft
        if tier.get("brunft_zyklus"):
            letzte_brunft = db.get_letztes_ereignis(tier["id"], farm_id, "brunft")
            if letzte_brunft:
                letztes_datum = date.fromisoformat(letzte_brunft["datum"])
                info["naechste_brunft"] = (
                    letztes_datum + timedelta(days=tier["brunft_zyklus"])
                ).strftime("%d.%m.%Y")
        
        # Erwartete Geburt
        letzte_besamung = db.get_letztes_ereignis(tier["id"], farm_id, "besamung")
        if letzte_besamung and tier.get("tragzeit"):
            letztes_datum = date.fromisoformat(letzte_besamung["datum"])
            info["erwartete_geburt"] = (
                letztes_datum + timedelta(days=tier["tragzeit"])
            ).strftime("%d.%m.%Y")
        
        tiere_mit_info.append(info)
    
    return render_template("dashboard.html",
                          farm=farm,
                          license=license,
                          tiere=tiere_mit_info,
                          tier_count=tier_count,
                          max_tiere=MAX_TIERE_FREE,
                          is_pro=license.get("is_pro", False) if license else False,
                          t=t)


@app.route("/tier/neu", methods=["GET", "POST"])
@require_farm
def tier_neu():
    farm_id = get_farm_id()
    tierarten = db.get_tierarten(farm_id)
    
    if request.method == "POST":
        # Tier-Limit prüfen
        count = db.get_tier_count(farm_id)
        is_pro = db.is_pro(farm_id)
        
        if count >= MAX_TIERE_FREE and not is_pro:
            flash(f"Limit erreicht! ({MAX_TIERE_FREE} Tiere kostenlos)", "warning")
            return redirect(url_for("dashboard", farm_id=farm_id))
        
        name = request.form.get("name", "").strip()
        if not name:
            flash("Name erforderlich", "error")
            return render_template("tier_form.html", tierarten=tierarten, t=t)
        
        ohrmarke = request.form.get("ohrmarke", "").strip()
        tierart_id = request.form.get("tierart_id")
        geburtsdatum = request.form.get("geburtsdatum", "").strip()
        
        db.add_tier(farm_id, name, ohrmarke, int(tierart_id) if tierart_id else None, geburtsdatum or None)
        flash(f"✅ {name} hinzugefügt", "success")
        return redirect(url_for("dashboard", farm_id=farm_id))
    
    return render_template("tier_form.html", tierarten=tierarten, t=t)


@app.route("/statistik")
@require_farm
@require_pro
def statistik():
    """Statistik & Auswertungen (PRO)"""
    farm_id = get_farm_id()
    
    kosten_stats = db.get_kosten_statistik(farm_id)
    besamungs_stats = db.get_besamungs_statistik(farm_id)
    
    return render_template("statistik.html",
                          kosten=kosten_stats,
                          besamungen=besamungs_stats,
                          t=t)


@app.route("/export/csv")
@require_farm
@require_pro
def export_csv():
    """CSV-Export (PRO)"""
    farm_id = get_farm_id()
    farm = db.get_farm(farm_id)
    tiere = db.get_alle_tiere(farm_id)
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Ohrmarke", "Tierart", "Status"])
    
    for tier in tiere:
        writer.writerow([
            tier["name"],
            tier["ohrmarke"] or "",
            tier["tierart_name"] or "",
            tier["status"]
        ])
    
    output.seek(0)
    return send_file(
        StringIO(output.getvalue()),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"tierkalb_{farm['name']}.csv"
    )


@app.route("/pro")
@require_farm
def pro():
    """Pro-Version Upgrade-Seite"""
    farm_id = get_farm_id()
    is_pro = db.is_pro(farm_id)
    
    return render_template("pro.html",
                          is_pro=is_pro,
                          price=PRO_PRICE,
                          farm_id=farm_id,
                          t=t)


@app.route("/pro/unlock", methods=["POST"])
@require_farm
def pro_unlock():
    """Pro mit Lizenz-Key freischalten"""
    farm_id = get_farm_id()
    license_key = request.form.get("license_key", "").strip()
    
    if not license_key:
        flash("Lizenz-Key erforderlich", "error")
        return redirect(url_for("pro", farm_id=farm_id))
    
    # Einfache Validierung (in Produktion: gegen API checken)
    if len(license_key) >= 20:
        db.unlock_pro(farm_id, license_key)
        flash("✅ Pro-Version aktiviert!", "success")
        return redirect(url_for("statistik", farm_id=farm_id))
    
    flash("❌ Ungültiger Lizenz-Key", "error")
    return redirect(url_for("pro", farm_id=farm_id))


# ─── Error Handler ────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", t=t), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html", t=t), 500


if __name__ == "__main__":
    db.init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
