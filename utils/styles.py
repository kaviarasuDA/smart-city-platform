"""
utils/styles.py
Centralised CSS injection and UI component helpers.
"""

import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS  – call once per page
# ─────────────────────────────────────────────────────────────────────────────

GLOBAL_CSS = """
<style>
/* ── Base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 40%, #24243e 100%);
    min-height: 100vh;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #1a2744 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label {
    color: #94a3b8 !important;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Main content ── */
.main .block-container {
    padding: 2rem 2.5rem;
    max-width: 1400px;
}

/* ── KPI Cards (gradient) ── */
.kpi-card {
    background: linear-gradient(135deg, var(--c1), var(--c2));
    border-radius: 16px;
    padding: 22px 20px;
    color: white;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
    border: 1px solid rgba(255,255,255,0.12);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: -40%;
    right: -20%;
    width: 160px;
    height: 160px;
    border-radius: 50%;
    background: rgba(255,255,255,0.07);
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 16px 48px rgba(0,0,0,0.45);
}
.kpi-icon   { font-size: 2rem; margin-bottom: 6px; }
.kpi-value  { font-size: 2.1rem; font-weight: 800; line-height: 1.1; }
.kpi-label  { font-size: 0.78rem; opacity: 0.85; text-transform: uppercase;
               letter-spacing: 0.08em; margin-top: 4px; }
.kpi-delta  { font-size: 0.75rem; margin-top: 8px; opacity: 0.9; }

/* ── Glass card ── */
.glass-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 24px;
    color: #e2e8f0;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.25);
}

/* ── Section header ── */
.section-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 1rem;
    padding-bottom: 8px;
    border-bottom: 2px solid rgba(99,102,241,0.5);
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── Page hero banner ── */
.page-hero {
    background: linear-gradient(135deg, rgba(99,102,241,0.15) 0%,
                rgba(139,92,246,0.15) 100%);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 20px;
    padding: 32px 36px;
    margin-bottom: 28px;
    color: white;
}
.page-hero h1 {
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0 0 8px;
    background: linear-gradient(90deg, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.page-hero p {
    color: #94a3b8;
    font-size: 1rem;
    margin: 0;
}

/* ── Alert banners ── */
.alert-critical {
    background: linear-gradient(135deg, rgba(239,68,68,0.2), rgba(220,38,38,0.1));
    border: 1px solid rgba(239,68,68,0.4);
    border-radius: 12px;
    padding: 14px 18px;
    color: #fca5a5;
    font-weight: 600;
    margin-bottom: 12px;
}
.alert-warning {
    background: linear-gradient(135deg, rgba(245,158,11,0.2), rgba(217,119,6,0.1));
    border: 1px solid rgba(245,158,11,0.4);
    border-radius: 12px;
    padding: 14px 18px;
    color: #fde68a;
    font-weight: 600;
    margin-bottom: 12px;
}
.alert-success {
    background: linear-gradient(135deg, rgba(16,185,129,0.2), rgba(5,150,105,0.1));
    border: 1px solid rgba(16,185,129,0.4);
    border-radius: 12px;
    padding: 14px 18px;
    color: #6ee7b7;
    font-weight: 600;
    margin-bottom: 12px;
}

/* ── Risk badge ── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 50px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.badge-critical { background: rgba(239,68,68,0.25);  color: #f87171; }
.badge-high     { background: rgba(249,115,22,0.25); color: #fb923c; }
.badge-medium   { background: rgba(245,158,11,0.25); color: #fbbf24; }
.badge-low      { background: rgba(16,185,129,0.25); color: #34d399; }

/* ── Plotly chart background ── */
.stPlotlyChart { border-radius: 14px; overflow: hidden; }

/* ── Dataframe ── */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* ── Sidebar logo ── */
.sidebar-logo {
    text-align: center;
    padding: 20px 0 10px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 16px;
}
.sidebar-logo h2 {
    font-size: 1rem;
    font-weight: 700;
    background: linear-gradient(90deg, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 8px 0 4px;
}
.sidebar-logo p {
    font-size: 0.7rem;
    color: #64748b !important;
    margin: 0;
}

/* ── Recommendation card ── */
.rec-card {
    background: rgba(99,102,241,0.1);
    border: 1px solid rgba(99,102,241,0.25);
    border-left: 4px solid #6366f1;
    border-radius: 10px;
    padding: 14px 18px;
    color: #c7d2fe;
    margin-bottom: 10px;
    font-size: 0.9rem;
}

/* ── Footer ── */
.footer {
    text-align: center;
    padding: 28px;
    color: #475569;
    font-size: 0.8rem;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin-top: 40px;
}
.footer span { color: #6366f1; }

/* ── Progress bar override ── */
.stProgress > div > div > div { background: linear-gradient(90deg,#6366f1,#8b5cf6); }

/* Hide Streamlit branding ── */
#MainMenu, footer { visibility: hidden; }
</style>
"""


def inject_global_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  COMPONENT HELPERS
# ─────────────────────────────────────────────────────────────────────────────

CARD_PRESETS = {
    "blue":    ("#3b82f6", "#1d4ed8"),
    "green":   ("#10b981", "#059669"),
    "red":     ("#ef4444", "#b91c1c"),
    "orange":  ("#f97316", "#c2410c"),
    "purple":  ("#8b5cf6", "#6d28d9"),
    "indigo":  ("#6366f1", "#4338ca"),
    "teal":    ("#14b8a6", "#0f766e"),
    "yellow":  ("#eab308", "#ca8a04"),
    "pink":    ("#ec4899", "#be185d"),
    "sky":     ("#0ea5e9", "#0284c7"),
}


def kpi_card(icon: str, label: str, value: str,
             delta: str = "", color: str = "blue") -> str:
    c1, c2 = CARD_PRESETS.get(color, ("#6366f1", "#4338ca"))
    delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ""
    return f"""
<div class="kpi-card" style="--c1:{c1};--c2:{c2};">
  <div class="kpi-icon">{icon}</div>
  <div class="kpi-value">{value}</div>
  <div class="kpi-label">{label}</div>
  {delta_html}
</div>"""


def page_hero(title: str, subtitle: str, icon: str = ""):
    st.markdown(f"""
<div class="page-hero">
  <h1>{icon} {title}</h1>
  <p>{subtitle}</p>
</div>""", unsafe_allow_html=True)


def section_header(title: str, icon: str = ""):
    st.markdown(
        f'<div class="section-header">{icon} {title}</div>',
        unsafe_allow_html=True
    )


def alert(msg: str, level: str = "warning"):
    cls = f"alert-{level}"
    icons = {"critical": "🚨", "warning": "⚠️", "success": "✅"}
    ico = icons.get(level, "ℹ️")
    st.markdown(f'<div class="{cls}">{ico} {msg}</div>', unsafe_allow_html=True)


def recommendation_card(text: str):
    st.markdown(f'<div class="rec-card">💡 {text}</div>', unsafe_allow_html=True)


def glass_card_open():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)


def glass_card_close():
    st.markdown('</div>', unsafe_allow_html=True)


def sidebar_brand():
    st.sidebar.markdown("""
<div class="sidebar-logo">
  <div style="font-size:2rem;">🏙️</div>
  <h2>SmartCity OS</h2>
  <p>Street Light Analytics Platform</p>
</div>""", unsafe_allow_html=True)


def page_footer():
    st.markdown("""
<div class="footer">
  Built with <span>Streamlit · Plotly · Folium · Pandas</span> &nbsp;|&nbsp;
  SmartCity OS v3.0 &nbsp;|&nbsp; © 2025 Urban Intelligence Division
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PLOTLY THEME
# ─────────────────────────────────────────────────────────────────────────────

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#e2e8f0"),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(
        bgcolor="rgba(255,255,255,0.05)",
        bordercolor="rgba(255,255,255,0.1)",
        borderwidth=1,
        font=dict(color="#cbd5e1"),
    ),
)

COLOR_SEQ = [
    "#6366f1", "#8b5cf6", "#ec4899", "#f97316",
    "#eab308", "#10b981", "#14b8a6", "#0ea5e9",
    "#f43f5e", "#a855f7",
]

STATUS_COLORS  = {"Working": "#10b981", "Faulty": "#ef4444"}
RISK_COLORS    = {
    "Critical": "#ef4444",
    "High":     "#f97316",
    "Medium":   "#eab308",
    "Low":      "#10b981",
}
PRIORITY_COLORS = {
    "Critical": "#ef4444",
    "High":     "#f97316",
    "Medium":   "#eab308",
    "Low":      "#10b981",
}
