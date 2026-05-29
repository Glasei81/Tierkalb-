# Tierart-Konfigurationen für Tierkalb v3.0

TIERARTEN = {
    "Rinder":   {"brunft": 21,   "tragzeit": 280, "label": "Kalben",      "emoji": "🐄"},
    "Schafe":   {"brunft": 17,   "tragzeit": 150, "label": "Lammzeit",    "emoji": "🐑"},
    "Schweine": {"brunft": 21,   "tragzeit": 114, "label": "Abferkelung", "emoji": "🐷"},
    "Ziegen":   {"brunft": 21,   "tragzeit": 150, "label": "Kitzung",     "emoji": "🐐"},
    "Hühner":   {"brunft": None, "tragzeit": 21,  "label": "Schlupf",     "emoji": "🐔"},
}

KOSTEN_TYPEN = [
    "Tierarzt",
    "Besamung",
    "Futter",
    "Medikamente",
    "Impfung",
    "Sonstiges",
]

EREIGNIS_TYPEN = [
    ("brunft",    "🌸 Brunft"),
    ("besamung",  "💉 Besamung"),
    ("geburt",    "🐣 Geburt"),
    ("impfung",   "💊 Impfung"),
    ("tierarzt",  "🩺 Tierarzt"),
    ("sonstiges", "📝 Sonstiges"),
]

I18N = {
    "de": {
        "willkommen":      "Willkommen zu Tierkalb",
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
        "willkommen":      "Welcome to Tierkalb",
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
