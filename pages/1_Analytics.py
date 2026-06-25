"""
pages/1_Analytics.py  ─  SmartCity OS  |  Advanced Analytics
Interactive Plotly charts: status distribution, voltage/current analysis,
area heatmap, fault trends, and drill-down insights.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data_utils import load_data, compute_kpis, area_ranking
from utils.styles import (
    inject_global_css, page_hero, section_header, sidebar_brand,
    page_footer, alert, PLOTLY_LAYOUT, COLOR_SEQ,
    STATUS_COLORS, RISK_COLORS,
)

# ── Page config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SmartCity OS · Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_global_css()

# ── Sidebar ─────────────────────────────────────────────────────────────────

sidebar_brand()
with st.sidebar:
    st.markdown("### 🔎 Analytics Filters")
    df_raw = load_data()
    all_areas = ["All Areas"] + sorted(df_raw["Area"].unique().tolist())
    selected_area = st.selectbox("Area", all_areas)
    chart_theme = st.selectbox("Chart Style", ["Dark Modern", "Minimal", "Vibrant"])
    show_raw = st.checkbox("Show Raw Data Table", value=False)

# ── Data ────────────────────────────────────────────────────────────────────

df = df_raw.copy()
if selected_area != "All Areas":
    df = df[df["Area"] == selected_area]

kpis = compute_kpis(df)

# ── Hero ─────────────────────────────────────────────────────────────────────

page_hero(
    "Advanced Analytics Center",
    "Interactive charts · Drill-down insights · Voltage & current profiling · Area comparison",
    "📊",
)

# ── Mini KPI strip ───────────────────────────────────────────────────────────

k1, k2, k3, k4, k5 = st.columns(5)
mini_style = "background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:14px;text-align:center;color:white;"

for col, lbl, val, color in [
    (k1, "Total", kpis["total"],          "#818cf8"),
    (k2, "Working", kpis["working"],      "#34d399"),
    (k3, "Faulty", kpis["faulty"],        "#f87171"),
    (k4, "Fault %", f"{kpis['fault_pct']}%", "#fbbf24"),
    (k5, "Health", f"{kpis['health_score']}%", "#22d3ee"),
]:
    with col:
        st.markdown(f"""
<div style="{mini_style}">
  <div style="font-size:1.6rem;font-weight:800;color:{color};">{val}</div>
  <div style="font-size:0.72rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.07em;">{lbl}</div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1 – Status Overview
# ═══════════════════════════════════════════════════════════════════════════

section_header("Status Distribution Analysis", "🔵")
col_l, col_r = st.columns(2)

with col_l:
    # Interactive Pie
    status_counts = df["Status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    fig_pie = px.pie(
        status_counts, names="Status", values="Count",
        color="Status",
        color_discrete_map=STATUS_COLORS,
        hole=0.55,
        title="Working vs Faulty Distribution",
    )
    fig_pie.update_traces(
        textposition="outside",
        textfont_size=13,
        pull=[0.04 if s == "Faulty" else 0 for s in status_counts["Status"]],
    )
    fig_pie.update_layout(**PLOTLY_LAYOUT, height=360, showlegend=True)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_r:
    # Grouped bar by area
    area_status = (
        df.groupby(["Area", "Status"])
        .size()
        .reset_index(name="Count")
    )
    fig_gb = px.bar(
        area_status, x="Area", y="Count", color="Status",
        color_discrete_map=STATUS_COLORS,
        barmode="group",
        title="Working vs Faulty by Area",
        text="Count",
    )
    fig_gb.update_traces(textposition="outside", textfont=dict(color="white"))
    fig_gb.update_layout(**PLOTLY_LAYOUT, height=360,
                          xaxis=dict(showgrid=False),
                          yaxis=dict(showgrid=False, gridcolor="rgba(255,255,255,0.06)"))
    st.plotly_chart(fig_gb, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2 – Voltage & Current Analysis
# ═══════════════════════════════════════════════════════════════════════════

section_header("Voltage & Current Profiling", "⚡")
v_col, c_col = st.columns(2)

with v_col:
    # Violin – voltage distribution by status
    fig_vol = px.violin(
        df, x="Status", y="Voltage", color="Status",
        color_discrete_map=STATUS_COLORS,
        box=True, points="all",
        title="Voltage Distribution by Status",
        hover_data=["Light_ID", "Area"],
    )
    fig_vol.update_layout(**PLOTLY_LAYOUT, height=360, showlegend=False)
    st.plotly_chart(fig_vol, use_container_width=True)

with c_col:
    # Scatter – Voltage vs Current (colour by status)
    fig_scat = px.scatter(
        df, x="Voltage", y="Current",
        color="Status", symbol="Area",
        color_discrete_map=STATUS_COLORS,
        size_max=14,
        title="Voltage vs Current (coloured by Status)",
        hover_data=["Light_ID", "Area", "Risk_Level"],
    )
    fig_scat.add_vline(x=200, line_dash="dash", line_color="#eab308",
                        annotation_text="Voltage Threshold",
                        annotation_font_color="#eab308")
    fig_scat.update_layout(**PLOTLY_LAYOUT, height=360)
    st.plotly_chart(fig_scat, use_container_width=True)

# ── Voltage histogram + Current bar ─────────────────────────────────────────

h1, h2 = st.columns(2)

with h1:
    fig_hist = px.histogram(
        df, x="Voltage", color="Status",
        color_discrete_map=STATUS_COLORS,
        nbins=12, title="Voltage Frequency Distribution",
        opacity=0.85,
    )
    fig_hist.update_layout(**PLOTLY_LAYOUT, height=300,
                             bargap=0.08,
                             xaxis=dict(showgrid=False),
                             yaxis=dict(gridcolor="rgba(255,255,255,0.06)"))
    st.plotly_chart(fig_hist, use_container_width=True)

with h2:
    # Area-wise average voltage bar
    avg_v = df.groupby("Area")["Voltage"].mean().reset_index()
    avg_v.columns = ["Area", "Avg_Voltage"]
    fig_avgv = px.bar(
        avg_v, x="Area", y="Avg_Voltage",
        color="Avg_Voltage",
        color_continuous_scale=["#ef4444", "#eab308", "#10b981"],
        title="Average Voltage per Area",
        text=avg_v["Avg_Voltage"].round(1),
    )
    fig_avgv.update_traces(textposition="outside", textfont=dict(color="white"))
    fig_avgv.add_hline(y=220, line_dash="dot", line_color="#6366f1",
                        annotation_text="Ideal 220V",
                        annotation_font_color="#818cf8")
    fig_avgv.update_layout(**PLOTLY_LAYOUT, height=300,
                             coloraxis_showscale=False,
                             xaxis=dict(showgrid=False),
                             yaxis=dict(gridcolor="rgba(255,255,255,0.06)"))
    st.plotly_chart(fig_avgv, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3 – Risk Heatmap
# ═══════════════════════════════════════════════════════════════════════════

section_header("Risk Score Heatmap", "🌡️")

heatmap_df = df.pivot_table(
    index="Area", columns="Status", values="Risk_Score", aggfunc="mean"
).fillna(0)

fig_heat = go.Figure(go.Heatmap(
    z=heatmap_df.values,
    x=heatmap_df.columns.tolist(),
    y=heatmap_df.index.tolist(),
    colorscale=[[0, "#10b981"], [0.5, "#eab308"], [1, "#ef4444"]],
    text=[[f"{v:.0f}" for v in row] for row in heatmap_df.values],
    texttemplate="%{text}",
    textfont=dict(size=14, color="white"),
    showscale=True,
    colorbar=dict(tickfont=dict(color="#e2e8f0")),
))
fig_heat.update_layout(**PLOTLY_LAYOUT, height=280,
                         title="Avg Risk Score by Area & Status",
                         xaxis=dict(showgrid=False),
                         yaxis=dict(showgrid=False))
st.plotly_chart(fig_heat, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4 – Drill-down: Area Deep Dive
# ═══════════════════════════════════════════════════════════════════════════

section_header("Area Deep Dive", "🔬")

area_list = sorted(df["Area"].unique())
drill_area = st.selectbox("Select Area for Deep Dive", area_list, key="drill")
area_df = df[df["Area"] == drill_area]

d1, d2, d3 = st.columns(3)
with d1:
    st.markdown(f"""
<div style="background:rgba(99,102,241,0.12);border:1px solid rgba(99,102,241,0.3);
border-radius:12px;padding:16px;text-align:center;color:white;">
  <div style="font-size:0.72rem;color:#94a3b8;text-transform:uppercase;">Lights in {drill_area}</div>
  <div style="font-size:2rem;font-weight:800;color:#818cf8;">{len(area_df)}</div>
</div>""", unsafe_allow_html=True)
with d2:
    faulty_cnt = (area_df["Status"] == "Faulty").sum()
    st.markdown(f"""
<div style="background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);
border-radius:12px;padding:16px;text-align:center;color:white;">
  <div style="font-size:0.72rem;color:#94a3b8;text-transform:uppercase;">Faulty Lights</div>
  <div style="font-size:2rem;font-weight:800;color:#f87171;">{faulty_cnt}</div>
</div>""", unsafe_allow_html=True)
with d3:
    avg_hs = area_df["Health_Score"].mean()
    st.markdown(f"""
<div style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);
border-radius:12px;padding:16px;text-align:center;color:white;">
  <div style="font-size:0.72rem;color:#94a3b8;text-transform:uppercase;">Avg Health Score</div>
  <div style="font-size:2rem;font-weight:800;color:#34d399;">{avg_hs:.0f}%</div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

fig_drill = make_subplots(
    rows=1, cols=2,
    subplot_titles=["Voltage Profile", "Current Profile"],
    horizontal_spacing=0.12,
)

fig_drill.add_trace(
    go.Bar(
        x=area_df["Light_ID"], y=area_df["Voltage"],
        marker_color=[STATUS_COLORS.get(s, "#94a3b8") for s in area_df["Status"]],
        name="Voltage",
        text=area_df["Voltage"],
        textposition="outside",
        textfont=dict(color="white", size=10),
    ), row=1, col=1
)
fig_drill.add_trace(
    go.Bar(
        x=area_df["Light_ID"], y=area_df["Current"],
        marker_color=[STATUS_COLORS.get(s, "#94a3b8") for s in area_df["Status"]],
        name="Current",
        text=area_df["Current"],
        textposition="outside",
        textfont=dict(color="white", size=10),
    ), row=1, col=2
)

fig_drill.update_layout(**PLOTLY_LAYOUT, height=340,
                          showlegend=False,
                          title=f"Per-Light Profile — {drill_area} Area")
st.plotly_chart(fig_drill, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5 – Insights Summary
# ═══════════════════════════════════════════════════════════════════════════

section_header("Analytical Insights", "🧠")

insights = []

if kpis["fault_pct"] > 30:
    insights.append(f"🔴 **Critical**: Fault rate {kpis['fault_pct']}% exceeds 30% threshold — urgent intervention needed.")
elif kpis["fault_pct"] > 15:
    insights.append(f"🟡 **Moderate**: {kpis['fault_pct']}% fault rate is above the 15% advisory level.")
else:
    insights.append(f"🟢 **Healthy**: Fault rate at {kpis['fault_pct']}% — within acceptable limits.")

low_v = (df["Voltage"] < 200).sum()
if low_v:
    insights.append(f"⚡ **Voltage Alert**: {low_v} lights operating below 200V — risk of LED driver failure.")

zero_curr = (df["Current"] == 0).sum()
if zero_curr:
    insights.append(f"🔋 **Dead Circuits**: {zero_curr} lights drawing 0A current — complete circuit failure suspected.")

if kpis["avg_current"] < 0.3:
    insights.append("📉 **Low Current Trend**: Network average current below 0.3A — possible ageing ballasts.")

insights.append(f"🏙️ **Hotspot**: {kpis['top_area']} zone requires priority attention with {kpis['top_area_cnt']} faults.")

for ins in insights:
    st.markdown(f"""
<div class="glass-card" style="padding:14px 20px;margin-bottom:8px;font-size:0.9rem;">
  {ins}
</div>""", unsafe_allow_html=True)

# ── Raw data table ──────────────────────────────────────────────────────────

if show_raw:
    section_header("Raw Data Explorer", "📋")
    st.dataframe(df, use_container_width=True, hide_index=True,
                  column_config={
                      "Health_Score": st.column_config.ProgressColumn(
                          "Health Score", min_value=0, max_value=100),
                      "Risk_Score": st.column_config.ProgressColumn(
                          "Risk Score", min_value=0, max_value=100),
                  })

page_footer()
