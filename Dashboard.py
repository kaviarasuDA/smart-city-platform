"""
Dashboard.py  ─  SmartCity OS  |  Executive Overview
Main entry point for the Streamlit multi-page application.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(__file__))

from utils.data_utils import load_data, compute_kpis, area_ranking
from utils.styles import (
    inject_global_css, kpi_card, page_hero, section_header,
    alert, recommendation_card, sidebar_brand, page_footer,
    PLOTLY_LAYOUT, COLOR_SEQ, STATUS_COLORS, RISK_COLORS,
)

# ── Page config ────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SmartCity OS · Executive Dashboard",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_global_css()

# ── Sidebar ────────────────────────────────────────────────────────────────

sidebar_brand()

with st.sidebar:
    st.markdown("### 🔎 Global Filters")
    df_raw = load_data()
    all_areas = ["All Areas"] + sorted(df_raw["Area"].unique().tolist())
    selected_area = st.selectbox("Filter by Area", all_areas)
    selected_status = st.selectbox("Filter by Status", ["All", "Working", "Faulty"])

    st.markdown("---")
    st.markdown("### 🔍 Search")
    search_id = st.text_input("Light ID", placeholder="e.g. SL001")

    st.markdown("---")
    st.markdown(f"""
<div style="font-size:0.72rem;color:#64748b;">
  🕒 Updated: {datetime.now().strftime('%d %b %Y, %H:%M:%S')}<br>
  📡 Data Source: Live CSV Feed<br>
  🖥️ Platform: SmartCity OS v3.0
</div>""", unsafe_allow_html=True)

# ── Apply filters ──────────────────────────────────────────────────────────

df = df_raw.copy()
if selected_area != "All Areas":
    df = df[df["Area"] == selected_area]
if selected_status != "All":
    df = df[df["Status"] == selected_status]

kpis = compute_kpis(df)

# ── Hero banner ────────────────────────────────────────────────────────────

page_hero(
    "Executive Command Center",
    f"Smart Street Light Analytics · {selected_area} · Real-time monitoring for municipal decision makers",
    "🏙️",
)

# ── System status banner ───────────────────────────────────────────────────

if kpis["fault_pct"] > 40:
    alert(f"CRITICAL ALERT — {kpis['faulty']} street lights are faulty ({kpis['fault_pct']}%). Immediate action required!", "critical")
elif kpis["fault_pct"] > 20:
    alert(f"WARNING — {kpis['faulty']} lights need attention. Fault rate at {kpis['fault_pct']}%.", "warning")
else:
    alert(f"System Operational — Network health at {kpis['health_score']}%. {kpis['faulty']} faults under monitoring.", "success")

# ── KPI Row 1 ──────────────────────────────────────────────────────────────

section_header("Key Performance Indicators", "📊")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(kpi_card("🚦", "Total Lights", str(kpis["total"]),
                         "Network-wide infrastructure count", "indigo"), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("✅", "Working Lights", str(kpis["working"]),
                         f"{kpis['health_score']}% operational", "green"), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("❌", "Faulty Lights", str(kpis["faulty"]),
                         f"{kpis['fault_pct']}% fault rate", "red"), unsafe_allow_html=True)
with c4:
    st.markdown(kpi_card("💚", "Network Health", f"{kpis['health_score']}%",
                         "Overall system wellness index", "teal"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── KPI Row 2 ──────────────────────────────────────────────────────────────

c5, c6, c7, c8 = st.columns(4)
with c5:
    st.markdown(kpi_card("⚡", "Avg Voltage", f"{kpis['avg_voltage']} V",
                         "Mean supply voltage", "sky"), unsafe_allow_html=True)
with c6:
    st.markdown(kpi_card("🔋", "Avg Current", f"{kpis['avg_current']} A",
                         "Mean operating current", "purple"), unsafe_allow_html=True)
with c7:
    st.markdown(kpi_card("💰", "Maintenance Cost", f"₹{kpis['total_cost']:,}",
                         "Estimated repair expenditure", "orange"), unsafe_allow_html=True)
with c8:
    st.markdown(kpi_card("🚨", "Critical Alerts", str(kpis["critical_cnt"]),
                         f"{kpis['high_cnt']} high-risk lights", "pink"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Search result ──────────────────────────────────────────────────────────

if search_id:
    section_header("Search Results", "🔍")
    results = df_raw[df_raw["Light_ID"].str.contains(search_id.strip(), case=False, na=False)]
    if len(results):
        st.markdown(f'<div class="alert-success">✅ {len(results)} record(s) found for "{search_id}"</div>',
                    unsafe_allow_html=True)
        st.dataframe(results, use_container_width=True, hide_index=True)
    else:
        st.markdown(f'<div class="alert-critical">❌ No light found with ID containing "{search_id}"</div>',
                    unsafe_allow_html=True)
    st.markdown("---")

# ── Charts row ─────────────────────────────────────────────────────────────

section_header("Network Overview Analytics", "📈")

left, right = st.columns([1, 1])

with left:
    # Donut – Status Distribution
    counts = df["Status"].value_counts().reset_index()
    counts.columns = ["Status", "Count"]
    fig_donut = go.Figure(go.Pie(
        labels=counts["Status"],
        values=counts["Count"],
        hole=0.65,
        marker_colors=[STATUS_COLORS.get(s, "#94a3b8") for s in counts["Status"]],
        textinfo="label+percent",
        textfont=dict(size=13, color="white"),
    ))
    fig_donut.add_annotation(
        text=f"<b>{kpis['total']}</b><br>Lights",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=18, color="white"),
    )
    fig_donut.update_layout(**PLOTLY_LAYOUT, title="Status Distribution",
                             height=320, showlegend=True)
    st.plotly_chart(fig_donut, use_container_width=True)

with right:
    # Bar – Area-wise fault count
    fault_by_area = (
        df[df["Status"] == "Faulty"]
        .groupby("Area")
        .size()
        .reset_index(name="Faults")
        .sort_values("Faults", ascending=True)
    )
    if len(fault_by_area):
        fig_bar = go.Figure(go.Bar(
            x=fault_by_area["Faults"],
            y=fault_by_area["Area"],
            orientation="h",
            marker=dict(
                color=fault_by_area["Faults"],
                colorscale=[[0, "#eab308"], [0.5, "#f97316"], [1, "#ef4444"]],
                showscale=False,
            ),
            text=fault_by_area["Faults"],
            textposition="outside",
            textfont=dict(color="white"),
        ))
        fig_bar.update_layout(**PLOTLY_LAYOUT, title="Faults by Area",
                               height=320,
                               xaxis=dict(showgrid=False),
                               yaxis=dict(showgrid=False))
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.markdown('<div class="alert-success">✅ No faulty lights in selected filter.</div>',
                    unsafe_allow_html=True)

# ── Health score gauge + Area ranking ──────────────────────────────────────

gauge_col, rank_col = st.columns([1, 2])

with gauge_col:
    section_header("Network Health Gauge", "💚")
    hs = kpis["health_score"]
    color = "#10b981" if hs >= 80 else "#eab308" if hs >= 60 else "#ef4444"
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=hs,
        delta={"reference": 90, "valueformat": ".1f"},
        number={"suffix": "%", "font": {"size": 36, "color": "white"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#94a3b8"},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 60],   "color": "rgba(239,68,68,0.15)"},
                {"range": [60, 80],  "color": "rgba(234,179,8,0.15)"},
                {"range": [80, 100], "color": "rgba(16,185,129,0.15)"},
            ],
            "threshold": {"line": {"color": "white", "width": 2}, "value": 90},
        },
    ))
    fig_gauge.update_layout(**PLOTLY_LAYOUT, height=280,
                             title=dict(text="Health Score", font=dict(color="white", size=14)))
    st.plotly_chart(fig_gauge, use_container_width=True)

with rank_col:
    section_header("Area Performance Ranking", "🏆")
    rank_df = area_ranking(df_raw if selected_area == "All Areas" else df)
    rank_display = rank_df[[
        "Rank", "Area", "Total", "Working", "Faulty",
        "Fault_Rate_%", "Health_%", "Avg_Voltage", "Avg_Current"
    ]].copy()
    rank_display["Avg_Voltage"] = rank_display["Avg_Voltage"].round(1)
    rank_display["Avg_Current"] = rank_display["Avg_Current"].round(3)
    st.dataframe(
        rank_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Health_%":      st.column_config.ProgressColumn("Health %", min_value=0, max_value=100),
            "Fault_Rate_%":  st.column_config.NumberColumn("Fault Rate %", format="%.1f%%"),
            "Rank":          st.column_config.NumberColumn("🏆 Rank"),
        }
    )

# ── Top alerts ─────────────────────────────────────────────────────────────

st.markdown("<br>", unsafe_allow_html=True)
section_header("Top Alerts & Recommendations", "🔔")

top_alerts = df[(df["Status"] == "Faulty") | (df["Risk_Level"] == "Critical")].head(5)
al, rec = st.columns([1, 1])

with al:
    if len(top_alerts):
        for _, row in top_alerts.iterrows():
            risk_color = {"Critical": "#ef4444", "High": "#f97316",
                          "Medium": "#eab308", "Low": "#10b981"}.get(row["Risk_Level"], "#94a3b8")
            st.markdown(f"""
<div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.25);
border-left:4px solid {risk_color};border-radius:10px;padding:12px 16px;
margin-bottom:8px;color:#e2e8f0;font-size:0.85rem;">
  <b>🔴 {row['Light_ID']}</b> — {row['Area']} Area &nbsp;
  <span style="background:rgba(239,68,68,0.2);color:#f87171;padding:2px 8px;
  border-radius:20px;font-size:0.7rem;font-weight:700;">{row['Risk_Level']}</span><br>
  <span style="color:#94a3b8;font-size:0.78rem;">
    Voltage: {row['Voltage']}V &nbsp;|&nbsp; Current: {row['Current']}A &nbsp;|&nbsp; Action: {row['Action']}
  </span>
</div>""", unsafe_allow_html=True)
    else:
        alert("No critical alerts in current filter. System performing well.", "success")

with rec:
    section_header("AI Recommendations", "🤖")
    if kpis["fault_pct"] > 30:
        recommendation_card("Deploy emergency maintenance crew to high-fault zones immediately.")
    if kpis["avg_voltage"] < 210:
        recommendation_card("Average supply voltage below threshold. Notify power utility provider.")
    if kpis["critical_cnt"] > 0:
        recommendation_card(f"{kpis['critical_cnt']} lights rated Critical — prioritize for same-day dispatch.")
    recommendation_card(f"Top fault area '{kpis['top_area']}' has {kpis['top_area_cnt']} faults — schedule area inspection.")
    recommendation_card("Consider predictive replacement for lights older than 8 years to reduce reactive maintenance.")

# ── Footer ─────────────────────────────────────────────────────────────────

page_footer()
