"""
pages/4_Map.py  ─  SmartCity OS  |  Smart GIS Map
Professional folium map with color-coded markers, rich popups,
area filters, legend panel, and fault overlay.
"""

import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster, MiniMap
from streamlit_folium import st_folium
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data_utils import load_data, compute_kpis
from utils.styles import (
    inject_global_css, page_hero, section_header, sidebar_brand,
    page_footer, alert, kpi_card, RISK_COLORS,
)

# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SmartCity OS · GIS Map",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_global_css()

# ── Sidebar ────────────────────────────────────────────────────────────────────

sidebar_brand()
with st.sidebar:
    st.markdown("### 🗺️ Map Controls")
    df_raw = load_data()
    all_areas = ["All Areas"] + sorted(df_raw["Area"].unique().tolist())
    selected_area   = st.selectbox("Filter by Area", all_areas)
    show_status     = st.multiselect("Show Status", ["Working", "Faulty"], default=["Working", "Faulty"])
    show_risk       = st.multiselect("Show Risk Levels",
                                     ["Critical", "High", "Medium", "Low"],
                                     default=["Critical", "High", "Medium", "Low"])
    cluster_markers = st.checkbox("Cluster Markers", value=False)
    map_tile        = st.selectbox("Map Style", [
        "CartoDB dark_matter",
        "CartoDB positron",
        "OpenStreetMap",
        "Stamen Terrain",
    ])
    zoom_level = st.slider("Default Zoom", 12, 18, 15)

    st.markdown("---")
    st.markdown("### 🎨 Legend")
    st.markdown("""
<div style="font-size:0.82rem;line-height:2;color:#e2e8f0;">
  <span style="color:#10b981;font-size:1.1rem;">●</span> Working Light<br>
  <span style="color:#ef4444;font-size:1.1rem;">●</span> Faulty Light<br>
  <span style="color:#eab308;font-size:1.1rem;">◆</span> Medium Risk<br>
  <span style="color:#f97316;font-size:1.1rem;">◆</span> High Risk<br>
  <span style="color:#ef4444;font-size:1.1rem;">★</span> Critical Risk<br>
</div>""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────

df = df_raw.copy()
if selected_area != "All Areas":
    df = df[df["Area"] == selected_area]
df = df[df["Status"].isin(show_status)]
df = df[df["Risk_Level"].isin(show_risk)]

kpis = compute_kpis(df)

# ── Hero ──────────────────────────────────────────────────────────────────────

page_hero(
    "Smart GIS Command Map",
    "Real-time geospatial visualisation · Color-coded fault markers · Interactive popups · Area intelligence",
    "📍",
)

# ── KPI strip ─────────────────────────────────────────────────────────────────

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(kpi_card("🚦", "Visible Lights", str(len(df)),
                         "On current map view", "indigo"), unsafe_allow_html=True)
with m2:
    st.markdown(kpi_card("✅", "Working", str(kpis["working"]),
                         "Operational lights", "green"), unsafe_allow_html=True)
with m3:
    st.markdown(kpi_card("❌", "Faulty", str(kpis["faulty"]),
                         "Needs attention", "red"), unsafe_allow_html=True)
with m4:
    st.markdown(kpi_card("🚨", "Critical", str(kpis["critical_cnt"]),
                         "Emergency dispatch needed", "pink"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Build Folium Map ──────────────────────────────────────────────────────────

section_header("Interactive Street Light Map", "🗺️")

if len(df) == 0:
    alert("No lights match the current filter settings. Adjust filters in the sidebar.", "warning")
else:
    center_lat = df["Latitude"].mean()
    center_lon = df["Longitude"].mean()

    # Map base
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_level,
        tiles=map_tile,
        control_scale=True,
    )

    # Mini map overlay
    MiniMap(toggle_display=True, tile_layer="CartoDB positron", zoom_level_offset=-6).add_to(m)

    # Marker container
    container = MarkerCluster(name="Street Lights") if cluster_markers else m

    def _risk_icon_color(risk_level: str, status: str) -> tuple:
        """Returns (color, icon_name) for folium DivIcon."""
        if status == "Working":
            return "#10b981", "lightbulb"
        color_map = {
            "Critical": "#ef4444",
            "High":     "#f97316",
            "Medium":   "#eab308",
            "Low":      "#6366f1",
        }
        return color_map.get(risk_level, "#94a3b8"), "exclamation-triangle"

    def _marker_html(color: str, status: str, risk: str) -> str:
        symbol = "✓" if status == "Working" else "✕"
        return f"""
        <div style="
            background:{color};
            border:2px solid white;
            border-radius:50%;
            width:24px;height:24px;
            display:flex;align-items:center;justify-content:center;
            color:white;font-size:11px;font-weight:bold;
            box-shadow:0 3px 10px rgba(0,0,0,0.5);
        ">{symbol}</div>"""

    def _popup_html(row) -> str:
        status_color = "#10b981" if row["Status"] == "Working" else "#ef4444"
        risk_color   = RISK_COLORS.get(row["Risk_Level"], "#94a3b8")
        return f"""
        <div style="font-family:Inter,sans-serif;min-width:220px;padding:4px;">
          <div style="background:linear-gradient(135deg,#1e1b4b,#312e81);
            border-radius:8px 8px 0 0;padding:10px 14px;margin:-4px -4px 10px;">
            <b style="color:white;font-size:14px;">🚦 {row['Light_ID']}</b>
          </div>
          <table style="width:100%;border-collapse:collapse;font-size:12px;color:#1e293b;">
            <tr><td style="padding:4px 6px;color:#64748b;">📍 Area</td>
                <td style="padding:4px 6px;font-weight:600;">{row['Area']}</td></tr>
            <tr style="background:#f8fafc;">
              <td style="padding:4px 6px;color:#64748b;">💡 Status</td>
              <td style="padding:4px 6px;"><b style="color:{status_color};">{row['Status']}</b></td>
            </tr>
            <tr><td style="padding:4px 6px;color:#64748b;">⚡ Voltage</td>
                <td style="padding:4px 6px;font-weight:600;">{row['Voltage']} V</td></tr>
            <tr style="background:#f8fafc;">
              <td style="padding:4px 6px;color:#64748b;">🔋 Current</td>
              <td style="padding:4px 6px;font-weight:600;">{row['Current']} A</td></tr>
            <tr><td style="padding:4px 6px;color:#64748b;">⚠️ Risk</td>
                <td style="padding:4px 6px;">
                  <span style="background:{risk_color}22;color:{risk_color};
                    padding:2px 8px;border-radius:12px;font-weight:700;font-size:11px;">
                    {row['Risk_Level']}
                  </span>
                </td></tr>
            <tr style="background:#f8fafc;">
              <td style="padding:4px 6px;color:#64748b;">📊 Risk Score</td>
              <td style="padding:4px 6px;font-weight:600;">{row['Risk_Score']}/100</td></tr>
            <tr><td style="padding:4px 6px;color:#64748b;">🔧 Action</td>
                <td style="padding:4px 6px;font-size:11px;color:#7c3aed;">{row['Action']}</td></tr>
          </table>
          <div style="margin-top:8px;font-size:10px;color:#94a3b8;text-align:center;">
            📡 {row['Latitude']:.4f}°N, {row['Longitude']:.4f}°E
          </div>
        </div>"""

    # Add markers
    for _, row in df.iterrows():
        color, _ = _risk_icon_color(row["Risk_Level"], row["Status"])
        icon_html = _marker_html(color, row["Status"], row["Risk_Level"])
        popup_html = _popup_html(row)

        marker = folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=folium.Tooltip(
                f"<b>{row['Light_ID']}</b> — {row['Status']} ({row['Risk_Level']})",
                style="font-family:Inter,sans-serif;font-size:12px;"
            ),
            icon=folium.DivIcon(html=icon_html, icon_size=(26, 26), icon_anchor=(13, 13)),
        )

        if cluster_markers:
            marker.add_to(container)
        else:
            marker.add_to(m)

    if cluster_markers:
        container.add_to(m)

    # ── Fault highlight circles ─────────────────────────────────────────────
    faulty_map = df[df["Status"] == "Faulty"]
    for _, row in faulty_map.iterrows():
        risk_color = RISK_COLORS.get(row["Risk_Level"], "#ef4444")
        folium.Circle(
            location=[row["Latitude"], row["Longitude"]],
            radius=40,
            color=risk_color,
            fill=True,
            fill_color=risk_color,
            fill_opacity=0.12,
            weight=1.5,
        ).add_to(m)

    # ── Legend ──────────────────────────────────────────────────────────────
    legend_html = """
    <div style="position:fixed;bottom:24px;right:24px;z-index:9999;
      background:rgba(15,12,41,0.92);backdrop-filter:blur(10px);
      border:1px solid rgba(255,255,255,0.15);border-radius:12px;
      padding:14px 18px;color:white;font-family:Inter,sans-serif;font-size:12px;
      box-shadow:0 8px 32px rgba(0,0,0,0.5);">
      <b style="font-size:13px;color:#818cf8;">🗺 Map Legend</b>
      <div style="margin-top:10px;line-height:2.1;">
        <span style="color:#10b981;">●</span> Working &nbsp;
        <span style="color:#ef4444;">●</span> Faulty<br>
        <span style="color:#ef4444;">◉</span> Critical Risk &nbsp;
        <span style="color:#f97316;">◉</span> High Risk<br>
        <span style="color:#eab308;">◉</span> Medium Risk &nbsp;
        <span style="color:#6366f1;">◉</span> Low Risk<br>
        <span style="color:#ef444455;font-size:18px;">●</span> Fault Radius Zone
      </div>
    </div>"""
    m.get_root().html.add_child(folium.Element(legend_html))

    # ── Layer control ───────────────────────────────────────────────────────
    folium.LayerControl(collapsed=False).add_to(m)

    # ── Render map ──────────────────────────────────────────────────────────
    map_data = st_folium(m, width="100%", height=580, returned_objects=[])

# ── Area summary table ────────────────────────────────────────────────────────

st.markdown("<br>", unsafe_allow_html=True)
section_header("Area Fault Summary", "📋")

area_summary = (
    df.groupby("Area")
    .agg(
        Total=("Light_ID",    "count"),
        Working=("Status",    lambda x: (x == "Working").sum()),
        Faulty=("Status",     lambda x: (x == "Faulty").sum()),
        Critical=("Risk_Level", lambda x: (x == "Critical").sum()),
        Avg_Risk=("Risk_Score", "mean"),
        Avg_Voltage=("Voltage", "mean"),
    )
    .reset_index()
)
area_summary["Fault_Rate_%"] = (area_summary["Faulty"] / area_summary["Total"] * 100).round(1)
area_summary["Avg_Risk"]     = area_summary["Avg_Risk"].round(1)
area_summary["Avg_Voltage"]  = area_summary["Avg_Voltage"].round(1)

st.dataframe(
    area_summary.sort_values("Faulty", ascending=False),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Fault_Rate_%": st.column_config.ProgressColumn("Fault Rate %", min_value=0, max_value=100),
        "Avg_Risk":     st.column_config.NumberColumn("Avg Risk Score"),
    }
)

# ── Faulty lights detail ──────────────────────────────────────────────────────

faulty_detail = df[df["Status"] == "Faulty"]
if len(faulty_detail):
    section_header(f"Faulty Light Locations ({len(faulty_detail)} records)", "🚨")
    st.dataframe(
        faulty_detail[["Light_ID", "Area", "Latitude", "Longitude",
                        "Voltage", "Current", "Risk_Level", "Action"]],
        use_container_width=True,
        hide_index=True,
    )

page_footer()
