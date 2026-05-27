"""
app.py — Tierkalb v3.0
Farm-Management: Tiere, Ereignisse, Kosten, Statistik, Export
"""

import os
import csv
from io import BytesIO, StringIO
from datetime import date, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, send_file
)

import database as db
from tierarten import TIERARTEN, I18N, KOSTEN_TYPEN, EREIGNIS_TYPEN

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24).hex())


# ─── Helpers ─────────────────────────────────────────────────────────────

def get_farm_id():
    if "farm_id" in session:
        return session["farm_id"]
    fid = request.args.get("farm_id") or request.form.get("farm_id")
    if fid:
        session["farm_id"] = fid
    return fid


def require_farm(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        fid = get_farm_id()
        if not fid or not db.get_farm(fid):
            return redirect(url_for("setup"))
        return f(*args, **kwargs)
    return decorated


def get_lang():
    fid = get_farm_id()
    return db.get_config(fid, "lang", "de") if fid else "de"


def t(key):
    lang = get_lang()
    return I18N.get(lang, I18N["de"]).get(key, key)


# ─── Setup ───────────────────────────────────────────────────────────────

@app.route("/")
def index():
    fid = get_farm_id()
    if fid and db.get_farm(fid):
        return redirect(url_for("dashboard"))
    return redirect(url_for("setup"))


@app.route("/setup", methods=["GET", "POST"])
def setup():
    if request.method == "POST":
        farm_name = request.form.get("farm_name", "").strip()
        owner_name = request.form.get("owner_name", "").strip()
        if not farm_name:
            flash("Bitte Betriebsnamen eingeben", "error")
            return render_template("setup.html", t=t, TIERARTEN=TIERARTEN)
        fid = db.create_farm(farm_name, owner_name)
        session["farm_id"] = fid
        for name, cfg in TIERARTEN.items():
            db.upsert_tierart(fid, name, cfg["brunft"], cfg["tragzeit"], cfg["emoji"])
        db.set_config(fid, "lang", request.form.get("lang", "de"))
        flash("Willkommen! Farm wurde erstellt.", "success")
        return redirect(url_for("dashboard"))
    return render_template("setup.html", t=t, TIERARTEN=TIERARTEN)


# ─── Dashboard ───────────────────────────────────────────────────────────

@app.route("/dashboard")
@require_farm
def dashboard():
    fid = get_farm_id()
    farm = db.get_farm(fid)
    tiere = db.get_alle_tiere(fid)
    upcoming = db.get_upcoming_geburten(fid, days=30)
    tier_count = db.get_tier_count(fid)
    gesamtkosten = db.get_gesamtkosten(fid)

    tiere_mit_info = []
    for tier in tiere:
        info = dict(tier)
        lb = db.get_letztes_ereignis(tier["id"], fid, "besamung")
        if lb and tier.get("tragzeit"):
            d = date.fromisoformat(lb["datum"])
            eb = d + timedelta(days=tier["tragzeit"])
            info["erwartete_geburt"] = eb.strftime("%d.%m.%Y")
            info["geburt_bald"] = (eb - date.today()).days <= 14
        tiere_mit_info.append(info)

    return render_template("dashboard.html",
        farm=farm, tiere=tiere_mit_info,
        upcoming=upcoming, tier_count=tier_count,
        gesamtkosten=gesamtkosten, t=t)


# ─── Tier CRUD ───────────────────────────────────────────────────────────

@app.route("/tier/neu", methods=["GET", "POST"])
@require_farm
def tier_neu():
    fid = get_farm_id()
    tierarten = db.get_tierarten(fid)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Name erforderlich", "error")
            return render_template("tier_form.html", tierarten=tierarten, t=t, tier=None)
        db.add_tier(
            fid, name,
            request.form.get("ohrmarke", "").strip(),
            int(request.form["tierart_id"]) if request.form.get("tierart_id") else None,
            request.form.get("geburtsdatum") or None,
            request.form.get("geschlecht", "weiblich"),
            request.form.get("notiz", "").strip(),
        )
        flash(f"{name} wurde hinzugefügt.", "success")
        return redirect(url_for("dashboard"))
    return render_template("tier_form.html", tierarten=tierarten, t=t, tier=None)


@app.route("/tier/<int:tier_id>")
@require_farm
def tier_detail(tier_id):
    fid = get_farm_id()
    tier = db.get_tier_by_id(tier_id, fid)
    if not tier:
        flash("Tier nicht gefunden.", "error")
        return redirect(url_for("dashboard"))
    ereignisse = db.get_ereignisse_fuer_tier(tier_id, fid)
    kosten = db.get_kosten_fuer_tier(tier_id, fid)
    kosten_gesamt = sum(k["betrag"] for k in kosten)

    erwartete_geburt = None
    lb = db.get_letztes_ereignis(tier_id, fid, "besamung")
    if lb and tier.get("tragzeit"):
        eb = date.fromisoformat(lb["datum"]) + timedelta(days=tier["tragzeit"])
        erwartete_geburt = eb.strftime("%d.%m.%Y")

    naechste_brunft = None
    lbr = db.get_letztes_ereignis(tier_id, fid, "brunft")
    if lbr and tier.get("brunft_zyklus"):
        nb = date.fromisoformat(lbr["datum"]) + timedelta(days=tier["brunft_zyklus"])
        naechste_brunft = nb.strftime("%d.%m.%Y")

    return render_template("tier_detail.html",
        tier=tier, ereignisse=ereignisse, kosten=kosten,
        kosten_gesamt=kosten_gesamt,
        erwartete_geburt=erwartete_geburt,
        naechste_brunft=naechste_brunft,
        t=t, KOSTEN_TYPEN=KOSTEN_TYPEN, EREIGNIS_TYPEN=EREIGNIS_TYPEN)


@app.route("/tier/<int:tier_id>/bearbeiten", methods=["GET", "POST"])
@require_farm
def tier_bearbeiten(tier_id):
    fid = get_farm_id()
    tier = db.get_tier_by_id(tier_id, fid)
    if not tier:
        return redirect(url_for("dashboard"))
    tierarten = db.get_tierarten(fid)
    if request.method == "POST":
        db.edit_tier(
            tier_id, fid,
            request.form.get("name", "").strip(),
            request.form.get("ohrmarke", "").strip(),
            int(request.form["tierart_id"]) if request.form.get("tierart_id") else None,
            request.form.get("geburtsdatum") or None,
            request.form.get("status", "Aktiv"),
            request.form.get("geschlecht", "weiblich"),
            request.form.get("notiz", "").strip(),
        )
        flash("Änderungen gespeichert.", "success")
        return redirect(url_for("tier_detail", tier_id=tier_id))
    return render_template("tier_form.html", tierarten=tierarten, t=t, tier=tier)


@app.route("/tier/<int:tier_id>/archivieren", methods=["POST"])
@require_farm
def tier_archivieren(tier_id):
    fid = get_farm_id()
    tier = db.get_tier_by_id(tier_id, fid)
    if tier:
        db.archiviere_tier(tier_id, fid)
        flash(f"{tier['name']} wurde archiviert.", "info")
    return redirect(url_for("dashboard"))


# ─── Ereignisse ──────────────────────────────────────────────────────────

@app.route("/tier/<int:tier_id>/ereignis/neu", methods=["GET", "POST"])
@require_farm
def ereignis_neu(tier_id):
    fid = get_farm_id()
    tier = db.get_tier_by_id(tier_id, fid)
    if not tier:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        db.add_ereignis(
            fid, tier_id,
            request.form.get("typ", "sonstiges"),
            request.form.get("datum", date.today().isoformat()),
            request.form.get("notiz", "").strip(),
        )
        flash("Ereignis eingetragen.", "success")
        return redirect(url_for("tier_detail", tier_id=tier_id))
    return render_template("ereignis_form.html",
        tier=tier, t=t,
        EREIGNIS_TYPEN=EREIGNIS_TYPEN,
        heute=date.today().isoformat())


@app.route("/tier/<int:tier_id>/ereignis/<int:ereignis_id>/loeschen", methods=["POST"])
@require_farm
def ereignis_loeschen(tier_id, ereignis_id):
    fid = get_farm_id()
    db.delete_ereignis(ereignis_id, fid)
    flash("Ereignis gelöscht.", "info")
    return redirect(url_for("tier_detail", tier_id=tier_id))


# ─── Kosten ──────────────────────────────────────────────────────────────

@app.route("/tier/<int:tier_id>/kosten/neu", methods=["GET", "POST"])
@require_farm
def kosten_neu(tier_id):
    fid = get_farm_id()
    tier = db.get_tier_by_id(tier_id, fid)
    if not tier:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        try:
            betrag = float(request.form.get("betrag", "0").replace(",", "."))
        except ValueError:
            betrag = 0.0
        db.add_kosten(
            fid, tier_id,
            request.form.get("typ", "Sonstiges"),
            betrag,
            request.form.get("datum", date.today().isoformat()),
            request.form.get("notiz", "").strip(),
        )
        flash(f"{betrag:.2f} € eingetragen.", "success")
        return redirect(url_for("tier_detail", tier_id=tier_id))
    return render_template("kosten_form.html",
        tier=tier, t=t,
        KOSTEN_TYPEN=KOSTEN_TYPEN,
        heute=date.today().isoformat())


@app.route("/tier/<int:tier_id>/kosten/<int:kosten_id>/loeschen", methods=["POST"])
@require_farm
def kosten_loeschen(tier_id, kosten_id):
    fid = get_farm_id()
    db.delete_kosten(kosten_id, fid)
    flash("Kosteneintrag gelöscht.", "info")
    return redirect(url_for("tier_detail", tier_id=tier_id))


# ─── Statistik ───────────────────────────────────────────────────────────

@app.route("/statistik")
@require_farm
def statistik():
    fid = get_farm_id()
    return render_template("statistik.html",
        kosten_pro_tier=db.get_kosten_pro_tier(fid),
        kosten_pro_typ=db.get_kosten_pro_typ(fid),
        kosten_pro_monat=db.get_kosten_pro_monat(fid, monate=12),
        besamungs_stats=db.get_besamungs_statistik(fid),
        gesamtkosten=db.get_gesamtkosten(fid),
        t=t)


# ─── Export ──────────────────────────────────────────────────────────────

@app.route("/export/csv")
@require_farm
def export_csv():
    fid = get_farm_id()
    farm = db.get_farm(fid)
    tiere = db.get_alle_tiere(fid, nur_aktiv=False)

    out = StringIO()
    w = csv.writer(out, delimiter=";")

    w.writerow(["=== TIERE ==="])
    w.writerow(["Name", "Ohrmarke", "Tierart", "Geburtsdatum", "Geschlecht", "Status", "Notiz"])
    for tier in tiere:
        w.writerow([tier["name"], tier["ohrmarke"] or "",
                    tier["tierart_name"] or "", tier["geburtsdatum"] or "",
                    tier.get("geschlecht") or "", tier["status"],
                    tier.get("notiz") or ""])

    w.writerow([])
    w.writerow(["=== EREIGNISSE ==="])
    w.writerow(["Tier", "Typ", "Datum", "Notiz"])
    for tier in tiere:
        for e in db.get_ereignisse_fuer_tier(tier["id"], fid):
            w.writerow([tier["name"], e["typ"], e["datum"], e["notiz"] or ""])

    w.writerow([])
    w.writerow(["=== KOSTEN ==="])
    w.writerow(["Tier", "Typ", "Betrag (EUR)", "Datum", "Notiz"])
    gesamt = 0.0
    for tier in tiere:
        for k in db.get_kosten_fuer_tier(tier["id"], fid):
            w.writerow([tier["name"], k["typ"],
                        f"{k['betrag']:.2f}", k["datum"], k["notiz"] or ""])
            gesamt += k["betrag"]
    w.writerow(["", "GESAMT", f"{gesamt:.2f}", "", ""])

    bio = BytesIO()
    bio.write(b"\xef\xbb\xbf")  # UTF-8 BOM für Excel
    bio.write(out.getvalue().encode("utf-8"))
    bio.seek(0)
    filename = f"tierkalb_{farm['name']}_{date.today().isoformat()}.csv"
    return send_file(bio, mimetype="text/csv", as_attachment=True, download_name=filename)


@app.route("/export/pdf")
@require_farm
def export_pdf():
    fid = get_farm_id()
    farm = db.get_farm(fid)
    tiere = db.get_alle_tiere(fid, nur_aktiv=False)

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle,
        Paragraph, Spacer, HRFlowable
    )

    bio = BytesIO()
    doc = SimpleDocTemplate(bio, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    GREEN = colors.HexColor("#2e7d32")
    BLUE  = colors.HexColor("#1565c0")
    LGREY = colors.HexColor("#f5f5f5")

    h1 = ParagraphStyle("h1", parent=styles["Title"], fontSize=18, spaceAfter=4)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12,
                        spaceBefore=10, spaceAfter=4, textColor=GREEN)
    h3 = ParagraphStyle("h3", parent=styles["Heading3"], fontSize=10,
                        spaceBefore=6, spaceAfter=2)
    normal = styles["Normal"]

    def make_table(data, col_widths, header_color):
        tbl = Table(data, colWidths=col_widths)
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), header_color),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LGREY]),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
            ("LEFTPADDING",   (0, 0), (-1, -1), 4),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
            ("TOPPADDING",    (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        return tbl

    story = []
    story.append(Paragraph(f"Tierkalb — {farm['name']}", h1))
    story.append(Paragraph(f"Bericht vom {date.today().strftime('%d.%m.%Y')}", normal))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Tiere", h2))
    data = [["Name", "Ohrmarke", "Tierart", "Geburtsdatum", "Status"]]
    for tier in tiere:
        emoji = tier.get("emoji") or ""
        data.append([
            tier["name"],
            tier["ohrmarke"] or "–",
            f"{emoji} {tier['tierart_name'] or '–'}",
            tier["geburtsdatum"] or "–",
            tier["status"],
        ])
    story.append(make_table(data, [4*cm, 3*cm, 4*cm, 3*cm, 3*cm], GREEN))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Kosten-Übersicht", h2))
    kpt = db.get_kosten_pro_tier(fid)
    gesamt = db.get_gesamtkosten(fid)
    kdata = [["Tier", "Gesamt (EUR)"]]
    for k in kpt:
        kdata.append([k["name"], f"{k['gesamt']:.2f}"])
    if kpt:
        kdata.append(["GESAMT", f"{gesamt:.2f}"])
        tbl = make_table(kdata, [12*cm, 5*cm], BLUE)
        tbl.setStyle(TableStyle([
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e3f2fd")),
        ]))
        story.append(tbl)
    else:
        story.append(Paragraph("Noch keine Kosten eingetragen.", normal))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Ereignisse", h2))
    for tier in tiere:
        ereignisse = db.get_ereignisse_fuer_tier(tier["id"], fid)
        if ereignisse:
            emoji = tier.get("emoji") or ""
            story.append(Paragraph(f"{emoji} {tier['name']}", h3))
            edata = [["Typ", "Datum", "Notiz"]]
            for e in ereignisse:
                edata.append([e["typ"].capitalize(), e["datum"], e["notiz"] or ""])
            story.append(make_table(edata, [3.5*cm, 3*cm, 10.5*cm],
                                    colors.HexColor("#4a148c")))
            story.append(Spacer(1, 0.2*cm))

    doc.build(story)
    bio.seek(0)
    filename = f"tierkalb_{farm['name']}_{date.today().isoformat()}.pdf"
    return send_file(bio, mimetype="application/pdf",
                     as_attachment=True, download_name=filename)


# ─── Einstellungen ───────────────────────────────────────────────────────

@app.route("/einstellungen", methods=["GET", "POST"])
@require_farm
def einstellungen():
    fid = get_farm_id()
    farm = db.get_farm(fid)
    if request.method == "POST":
        db.set_config(fid, "lang", request.form.get("lang", "de"))
        db.set_config(fid, "telegram_token",
                      request.form.get("telegram_token", "").strip())
        db.set_config(fid, "telegram_chat_id",
                      request.form.get("telegram_chat_id", "").strip())
        flash("Einstellungen gespeichert.", "success")
        return redirect(url_for("einstellungen"))
    return render_template("einstellungen.html",
        farm=farm,
        lang=db.get_config(fid, "lang", "de"),
        telegram_token=db.get_config(fid, "telegram_token", ""),
        telegram_chat_id=db.get_config(fid, "telegram_chat_id", ""),
        t=t)


# ─── Error Handler ───────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", t=t), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html", t=t), 500


if __name__ == "__main__":
    db.init_db()
    from telegram_bot import start_scheduler
    start_scheduler(app)
    # PORT-Umgebungsvariable für Railway/Cloud (Standard: 5000 lokal)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
