# Tierart-Konfigurationen für Tierkalb v2.0

TIERARTEN = {
    "Rinder":   {"brunft": 21,   "tragzeit": 280, "label": "Kalben",      "emoji": "🐄"},
    "Schafe":   {"brunft": 17,   "tragzeit": 150, "label": "Lammzeit",    "emoji": "🐑"},
    "Schweine": {"brunft": 21,   "tragzeit": 114, "label": "Abferkelung", "emoji": "🐷"},
    "Ziegen":   {"brunft": 21,   "tragzeit": 150, "label": "Kitzung",     "emoji": "🐐"},
    "Hühner":   {"brunft": None, "tragzeit": 21,  "label": "Schlupf",     "emoji": "🐔"},
}

# Mehrsprachigkeit
I18N = {
    "de": {
        "willkommen":      "Willkommen zu Tierkalb",
        "dashboard":       "Dashboard",
        "statistik":       "Statistik",
        "berichte":        "Berichte",
        "einstellungen":   "Einstellungen",
        "pro_version":     "Pro-Version",
        "kosten_analyse":  "Kosten-Analyse",
        "besamungen":      "Besamungen",
        "kalbungen":       "Kalbungen",
        "erfolgsrate":     "Erfolgsrate",
        "export":          "Exportieren",
        "pro_required":    "Pro-Version erforderlich",
        "limit_free":      "15 Tiere kostenlos",
        "unlimited_pro":   "Unbegrenzt mit Pro",
        "buy_now":         "Jetzt upgraden",
    },
    "en": {
        "willkommen":      "Welcome to Animalcal",
        "dashboard":       "Dashboard",
        "statistik":       "Statistics",
        "berichte":        "Reports",
        "einstellungen":   "Settings",
        "pro_version":     "Pro Version",
        "kosten_analyse":  "Cost Analysis",
        "besamungen":      "Inseminations",
        "kalbungen":       "Births",
        "erfolgsrate":     "Success Rate",
        "export":          "Export",
        "pro_required":    "Pro version required",
        "limit_free":      "15 animals free",
        "unlimited_pro":   "Unlimited with Pro",
        "buy_now":         "Upgrade now",
    },
}

MAX_TIERE_FREE = 15
PRO_PRICE = 19.99
