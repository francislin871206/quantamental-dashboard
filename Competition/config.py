"""
Configuration for Revolution Stock Selector Dashboard
"""

# ─── Default Ticker Universe ──────────────────────────────────────────────────
# AI / Technology sector
AI_TECH_TICKERS = ["PLTR", "AI", "IONQ", "BBAI", "SOUN", "UPST", "PATH", "RKLB",
                   "SMCI", "SNOW", "DDOG", "MDB", "NET", "CRWD", "ZS"]

# Biotech / Healthcare
BIOTECH_TICKERS = ["CRSP", "NTLA", "BEAM", "EDIT", "MRNA", "ARVN", "RCKT", "DNLI",
                   "REGN", "VRTX", "EXAS", "INCY", "SRPT", "PCVX", "MDGL"]

# Fintech / Disruptive Finance
FINTECH_TICKERS = ["SOFI", "AFRM", "HOOD", "COIN", "NU", "BILL", "FOUR", "TOST",
                   "SQ", "MELI", "PYPL", "ADYEY", "RELY", "PAGS", "STNE"]

# Energy / Clean Tech
CLEANTECH_TICKERS = ["ENPH", "SEDG", "FSLR", "RUN", "PLUG", "BE", "CHPT", "QS",
                     "NOVA", "ARRY", "STEM", "ENVX", "SHLS", "DQ", "MAXN"]

# Semiconductors & Hardware
SEMI_TICKERS = ["AMD", "NVDA", "MRVL", "AVGO", "ON", "WOLF", "ACLS", "AEHR",
                "LSCC", "SITM", "CEVA", "FORM", "INDI", "ALGM", "RMBS"]

# EV & Autonomous Vehicles
EV_TICKERS = ["TSLA", "RIVN", "LCID", "NIO", "XPEV", "LI", "GOEV", "RIDE",
              "LAZR", "LIDR", "INVZ", "OUST", "MVIS", "ASTS", "LUNR"]

# Cybersecurity
CYBER_TICKERS = ["PANW", "FTNT", "CYBR", "OKTA", "S", "TENB", "QLYS", "RPD",
                 "VRNS", "SAIL", "RDWR", "RBRK", "CVLT", "MNDT", "NLTX"]

# Consumer / Retail Disruptors
CONSUMER_TICKERS = ["SHOP", "ROKU", "PINS", "SNAP", "DUOL", "DKNG", "ABNB", "DASH",
                    "CHWY", "BROS", "CAVA", "CELH", "HIMS", "ONON", "BIRK"]

# All sectors combined
DEFAULT_UNIVERSE = AI_TECH_TICKERS + BIOTECH_TICKERS + FINTECH_TICKERS + CLEANTECH_TICKERS

# ─── Full US Universe for Auto-Scan (120+ stocks) ────────────────────────────
FULL_US_UNIVERSE = (AI_TECH_TICKERS + BIOTECH_TICKERS + FINTECH_TICKERS
                    + CLEANTECH_TICKERS + SEMI_TICKERS + EV_TICKERS
                    + CYBER_TICKERS + CONSUMER_TICKERS)

SECTOR_MAP = {
    "🤖 AI & Technology": AI_TECH_TICKERS,
    "🧬 Biotech & Healthcare": BIOTECH_TICKERS,
    "💳 Fintech & Disruptive Finance": FINTECH_TICKERS,
    "⚡ Clean Energy & Tech": CLEANTECH_TICKERS,
    "🔬 Semiconductors": SEMI_TICKERS,
    "🚗 EV & Autonomous": EV_TICKERS,
    "🛡️ Cybersecurity": CYBER_TICKERS,
    "🛒 Consumer Disruptors": CONSUMER_TICKERS,
    "🌐 All Sectors": DEFAULT_UNIVERSE,
    "🔥 Full US Universe (120+)": FULL_US_UNIVERSE,
}

# ─── Default Scoring Weights ─────────────────────────────────────────────────
DEFAULT_WEIGHTS = {
    "sentiment": 0.30,
    "catalyst": 0.25,
    "insider": 0.15,
    "options": 0.15,
    "technical": 0.15,
}

# ─── Chart Theme ──────────────────────────────────────────────────────────────
COLORS = {
    "bg_primary": "#0a0a1a",
    "bg_secondary": "#111128",
    "bg_card": "#1a1a3e",
    "accent_1": "#6c63ff",
    "accent_2": "#00d4aa",
    "accent_3": "#ff6b9d",
    "accent_4": "#ffd93d",
    "text_primary": "#e8e8f0",
    "text_secondary": "#8888aa",
    "positive": "#00d4aa",
    "negative": "#ff4757",
    "neutral": "#8888aa",
    "gradient_start": "#6c63ff",
    "gradient_end": "#00d4aa",
}

PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": COLORS["bg_primary"],
        "plot_bgcolor": COLORS["bg_secondary"],
        "font": {"color": COLORS["text_primary"], "family": "Inter, sans-serif"},
        "xaxis": {"gridcolor": "#222244", "zerolinecolor": "#222244"},
        "yaxis": {"gridcolor": "#222244", "zerolinecolor": "#222244"},
    }
}
