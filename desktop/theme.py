"""
Konfigurimet e temave, ngjyrave dhe fonteve per aplikacionin Desktop CustomTkinter.
100% të sinkronizuara me GUI.java.
"""

# Ngjyrat kryesore
PRIMARY_COLOR = "#2980b9"
PRIMARY_HOVER = "#3498db"

ACCENT_COLOR = "#2c3e50"
ACCENT_HOVER = "#34495e"

SUCCESS_COLOR = "#27ae60"
SUCCESS_HOVER = "#2ecc71"

DANGER_COLOR = "#c0392b"
DANGER_HOVER = "#e74c3c"

WARNING_COLOR = "#d35400"
WARNING_HOVER = "#e67e22"

PRICE_COLOR = "#f39c12"

# Ngjyrat e kategorive te artikujve (identike me Java GUI.java)
CATEGORY_COLORS = {
    "Pije": {"bg": "#3498db", "hover": "#2980b9"},
    "Kafe": {"bg": "#8d6e63", "hover": "#6d4c41"},
    "Ushqim": {"bg": "#e74c3c", "hover": "#c0392b"},
    "Embëlsirë": {"bg": "#e67e22", "hover": "#d35400"},
}

# Fontet
FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 16, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 13, "bold")
FONT_BODY = (FONT_FAMILY, 11)
FONT_BODY_BOLD = (FONT_FAMILY, 11, "bold")
FONT_TOTAL = (FONT_FAMILY, 22, "bold")
FONT_RECEIPT = ("Consolas", 12, "bold")
