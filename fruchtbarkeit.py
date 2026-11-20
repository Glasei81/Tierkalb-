"""
fruchtbarkeit.py — Fruchtbarkeits-Ablauf je Tier und gemeinsame Terminliste.

Ablauf nach der Besamung (Werte je Tierart in den Einstellungen änderbar):
  Tag 21 (= Brunftzyklus): auf Stierigkeit achten → wieder stierig = nachbesamen
  Tag 28: Trächtigkeitsuntersuchung (TU) → trächtig / nicht trächtig
  trächtig: Kalbung nach der Tragzeit (Fleckvieh 290 Tage)

Dashboard, Tierseite, Telegram-/status und Morgenmeldung nutzen alle diese Datei,
damit überall dieselben Termine stehen.
"""

from datetime import date, timedelta

TK_POS = "tk_pos"          # Ereignis: TU-Ergebnis trächtig
TK_NEG = "tk_neg"          # Ereignis: TU-Ergebnis nicht trächtig

KONTROLLE_FENSTER = 3      # Stierigkeit rund um Tag 21: ± so viele Tage
TU_FENSTER = 7             # TU gilt bis Tag 28 + 7 als fällig, danach "Ergebnis fehlt"
TU_ANNAHME_TAG = 60        # ohne TU-Ergebnis und ohne Brunft: ab hier als trächtig angenommen
                           # (wichtig für nachgetragene ältere Besamungen)
NACHBESAMEN_TAGE = 2       # so lange nach eingetragener Brunft gilt "jetzt nachbesamen"
UMRINDERN_AB_TAG = 5       # Brunft frühestens so viele Tage nach Besamung zählt als "wieder stierig"

# Reihenfolge innerhalb eines Tages: wichtiger zuerst
PRIO = {"nachbesamen": 0, "tk_fehlt": 0, "kalbung_ueberfaellig": 0,
        "kontrolle": 1, "tu": 1, "kalbung": 2, "brunft": 3}


def _d(s):
    return s if isinstance(s, date) else date.fromisoformat(s)


def _fmt(d):
    return d.strftime("%d.%m.%Y")


def ablauf(tier, ereignisse, heute=None):
    """Status und Termine für ein Tier.

    tier: dict mit geschlecht, brunft_zyklus, tragzeit, tk_tag (aus get_alle_tiere)
    ereignisse: Liste von dicts mit typ und datum (Reihenfolge egal)
    Rückgabe: {"status", "text", "termine": [...], "besamung", "tag", "kalbung"}
    """
    heute = heute or date.today()
    zyklus = tier.get("brunft_zyklus") or 0
    tragzeit = tier.get("tragzeit") or 0
    tk_tag = tier.get("tk_tag") or 0
    res = {"status": None, "text": "", "termine": [],
           "besamung": None, "tag": None, "kalbung": None}
    if tier.get("geschlecht") == "männlich" or tier.get("kategorie") in ("kalb", "stier") or not tragzeit:
        return res

    ev = sorted(((e["typ"], _d(e["datum"])) for e in ereignisse if e.get("datum")),
                key=lambda x: x[1])

    def letzte(typ, nach=None):
        ds = [d for t, d in ev if t == typ and (nach is None or d > nach)]
        return ds[-1] if ds else None

    def termin(datum, art, text):
        res["termine"].append({"datum": datum, "art": art, "text": text,
                               "prio": PRIO.get(art, 5), "tier": tier})

    def offen(refs, vorspann):
        refs = [r for r in refs if r]
        res["status"] = "offen"
        if not refs or not zyklus:
            res["text"] = f"{vorspann} — noch keine Brunft eingetragen"
            return res
        n = max(refs) + timedelta(days=zyklus)
        while n < heute - timedelta(days=2):
            n += timedelta(days=zyklus)
        res["text"] = f"{vorspann} — nächste Brunft ca. {_fmt(n)}"
        termin(n, "brunft", "Brunft erwartet, auf Stierigkeit achten")
        return res

    def kalbung(b, bestaetigt):
        k = b + timedelta(days=tragzeit)
        res["kalbung"] = k
        if k < heute:
            termin(k, "kalbung_ueberfaellig", "Kalbung überfällig? Geburt eintragen")
        else:
            termin(k, "kalbung", "Kalbung erwartet" + ("" if bestaetigt else " (nicht bestätigt)"))
        return k

    lg = letzte("geburt")
    b = letzte("besamung", nach=lg)
    if not b:
        vorspann = "offen" if not lg else f"offen seit Kalbung {_fmt(lg)}"
        return offen([letzte("brunft", nach=lg)], vorspann)

    tag = (heute - b).days
    res["besamung"], res["tag"] = b, tag
    vor_besamung = b - timedelta(days=1)
    kandidaten = [(d, art) for art, d in (
        ("pos", letzte(TK_POS, nach=vor_besamung)),
        ("neg", letzte(TK_NEG, nach=vor_besamung)),
        ("brunft", letzte("brunft", nach=b + timedelta(days=UMRINDERN_AB_TAG - 1))),
    ) if d]
    ergebnis = max(kandidaten) if kandidaten else None

    if ergebnis and ergebnis[1] == "brunft":
        br = ergebnis[0]
        if (heute - br).days <= NACHBESAMEN_TAGE:
            res["status"] = "nachbesamen"
            res["text"] = f"besamt {_fmt(b)}, am {_fmt(br)} wieder stierig — nachbesamen!"
            termin(br, "nachbesamen", "wieder stierig: nachbesamen!")
            return res
        return offen([br], f"umgerindert am {_fmt(br)}, nicht nachbesamt")

    if ergebnis and ergebnis[1] == "neg":
        # Brunftrhythmus läuft ab der Besamung (bzw. letzten Brunft) weiter, nicht ab dem TU-Tag
        return offen([b, letzte("brunft", nach=b)], f"nicht trächtig (TU {_fmt(ergebnis[0])})")

    if ergebnis and ergebnis[1] == "pos":
        res["status"] = "traechtig"
        k = kalbung(b, bestaetigt=True)
        res["text"] = f"trächtig (TU {_fmt(ergebnis[0])}) — Kalbung ca. {_fmt(k)}"
        return res

    # besamt, noch kein Ergebnis
    if zyklus and tag <= zyklus + KONTROLLE_FENSTER:
        res["status"] = "besamt"
        res["text"] = f"besamt {_fmt(b)} (Tag {tag})"
        termin(b + timedelta(days=zyklus), "kontrolle", f"Auf Stierigkeit achten (Tag {zyklus})")
        if tk_tag:
            termin(b + timedelta(days=tk_tag), "tu", f"Trächtigkeitsuntersuchung (Tag {tk_tag})")
        return res
    if tk_tag and tag <= tk_tag + TU_FENSTER:
        res["status"] = "besamt"
        res["text"] = f"besamt {_fmt(b)} (Tag {tag}), nicht umgerindert"
        termin(b + timedelta(days=tk_tag), "tu", f"Trächtigkeitsuntersuchung (Tag {tk_tag})")
        return res
    if tk_tag and tag <= TU_ANNAHME_TAG:
        res["status"] = "tk_fehlt"
        res["text"] = f"besamt {_fmt(b)} (Tag {tag}) — Ergebnis der Untersuchung fehlt"
        termin(b + timedelta(days=tk_tag), "tk_fehlt", "Ergebnis Trächtigkeitsuntersuchung eintragen")
        return res
    res["status"] = "traechtig_angenommen"
    k = kalbung(b, bestaetigt=False)
    res["text"] = f"vermutlich trächtig (besamt {_fmt(b)}, keine TU eingetragen) — Kalbung ca. {_fmt(k)}"
    return res


def herde(tiere, ereignisse_je_tier, heute=None):
    """Ablauf für alle Tiere. Rückgabe: {tier_id: ablauf}, sortierte Terminliste."""
    heute = heute or date.today()
    abl = {t["id"]: ablauf(t, ereignisse_je_tier.get(t["id"], []), heute) for t in tiere}
    termine = sorted((tm for a in abl.values() for tm in a["termine"]),
                     key=lambda tm: (tm["datum"], tm["prio"], tm["tier"]["name"]))
    return abl, termine


def gruppieren(termine, heute=None):
    """Teilt die Terminliste in überfällig / heute / nächste 7 Tage / später."""
    heute = heute or date.today()
    g = {"ueberfaellig": [], "heute": [], "woche": [], "spaeter": []}
    for tm in termine:
        if tm["art"] in ("tk_fehlt", "kalbung_ueberfaellig"):
            g["ueberfaellig"].append(tm)
        elif tm["datum"] <= heute:
            g["heute"].append(tm)
        elif tm["datum"] <= heute + timedelta(days=7):
            g["woche"].append(tm)
        else:
            g["spaeter"].append(tm)
    for liste in g.values():
        liste.sort(key=lambda tm: (tm["prio"], tm["datum"]))
    g["spaeter"].sort(key=lambda tm: tm["datum"])
    return g


def wann(tm, heute=None):
    """Kurze Zeitangabe für einen Termin, z.B. 'heute', 'morgen', 'in 5 Tagen', 'seit 2 Tagen'."""
    heute = heute or date.today()
    n = (tm["datum"] - heute).days
    if n == 0:
        return "heute"
    if n == 1:
        return "morgen"
    if n > 1:
        return f"in {n} Tagen"
    if n == -1:
        return "seit gestern"
    return f"seit {-n} Tagen"
