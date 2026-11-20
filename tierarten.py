# Tierart-Konfigurationen für HerdenPilot
# Voreinstellungen für neue Betriebe; je Betrieb in den Einstellungen änderbar.
# Rinder: Tragzeit 290 Tage (Fleckvieh), Brunft-Kontrolle Tag 21, Trächtigkeitsuntersuchung Tag 28.

TIERARTEN = {
    "Rinder":   {"brunft": 21,   "tragzeit": 290, "tk_tage": 28, "label": "Kalben",      "emoji": "🐄"},
    "Schafe":   {"brunft": 17,   "tragzeit": 150, "tk_tage": 20, "label": "Lammzeit",    "emoji": "🐑"},
    "Schweine": {"brunft": 21,   "tragzeit": 114, "tk_tage": 21, "label": "Abferkelung", "emoji": "🐷"},
    "Ziegen":   {"brunft": 21,   "tragzeit": 150, "tk_tage": 20, "label": "Kitzung",     "emoji": "🐐"},
}

KOSTEN_TYPEN = [
    "Tierarzt",
    "Besamung",
    "Futter",
    "Medikamente",
    "Sonstiges",
]

EREIGNIS_TYPEN = [
    ("brunft",    "🌸 Brunft"),
    ("besamung",  "💉 Besamung"),
    ("tk_pos",    "✅ TU: trächtig"),
    ("tk_neg",    "❌ TU: nicht trächtig"),
    ("geburt",    "🐣 Geburt"),
    ("tierarzt",  "🩺 Tierarzt / Impfung"),
    ("sonstiges", "📝 Sonstiges"),
]

# Anzeige-Namen aller Ereignisse (auch ältere, z.B. "impfung" aus früheren Versionen)
EREIGNIS_LABEL = {
    "brunft":    "🌸 Brunft",
    "besamung":  "💉 Besamung",
    "tk_pos":    "✅ Trächtigkeitsuntersuchung: trächtig",
    "tk_neg":    "❌ Trächtigkeitsuntersuchung: nicht trächtig",
    "geburt":    "🐣 Geburt",
    "tierarzt":  "🩺 Tierarzt",
    "impfung":   "💊 Impfung",
    "sonstiges": "📝 Sonstiges",
}

I18N = {
    "de": {
        "willkommen":      "Willkommen bei HerdenPilot",
        "dashboard":       "Dashboard",
        "statistik":       "Statistik",
        "einstellungen":   "Einstellungen",
        "tiere":           "Tiere",
        "neues_tier":      "Neues Tier",
        "bearbeiten":      "Bearbeiten",
        "loeschen":        "Löschen",
        "archivieren":     "Archivieren",
        "speichern":       "Speichern",
        "abbrechen":       "Abbrechen",
        "ereignisse":      "Ereignisse",
        "kosten":          "Kosten",
        "neues_ereignis":  "Ereignis eintragen",
        "neue_kosten":     "Kosten eintragen",
        "export":          "Exportieren",
        "kosten_analyse":  "Kosten-Analyse",
        "besamungen":      "Besamungen",
        "geburten":        "Geburten",
        "erfolgsrate":     "Erfolgsrate",
        "gesamt":          "Gesamt",
        "keine_daten":     "Noch keine Daten vorhanden",
    },
    "en": {
        "willkommen":      "Welcome to HerdenPilot",
        "dashboard":       "Dashboard",
        "statistik":       "Statistics",
        "einstellungen":   "Settings",
        "tiere":           "Animals",
        "neues_tier":      "New Animal",
        "bearbeiten":      "Edit",
        "loeschen":        "Delete",
        "archivieren":     "Archive",
        "speichern":       "Save",
        "abbrechen":       "Cancel",
        "ereignisse":      "Events",
        "kosten":          "Costs",
        "neues_ereignis":  "Add Event",
        "neue_kosten":     "Add Cost",
        "export":          "Export",
        "kosten_analyse":  "Cost Analysis",
        "besamungen":      "Inseminations",
        "geburten":        "Births",
        "erfolgsrate":     "Success Rate",
        "gesamt":          "Total",
        "keine_daten":     "No data available yet",
    },
}
