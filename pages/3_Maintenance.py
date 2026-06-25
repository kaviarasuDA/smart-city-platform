"""
pages/3_Maintenance.py  ─  SmartCity OS  |  Maintenance Intelligence
Priority engine, cost estimation dashboard, repair scheduling,
technician workload, resource planning, and actionable insights.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data_utils import load_data, compute_kpis
from utils.styles import (
    inject_global_css, page_hero, section_header, sidebar_brand,
    page_footer, alert, recommendation_card, kpi_card,
    PLOTLY_LAYOUT, COLOR_SEQ, PRIORITY_COLORS,
)

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SmartCity OS · Maintenance",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_global_css()

# ── Sidebar ───────────────────────────────────────────────────────────────────

sidebar_brand()
with st.sidebar:
    st.markdown("### ⚙️ Maintenance Settings")
    df_raw = load_data()
    all_areas = ["All Areas"] + sorted(df_raw["Area"].unique().tolist())
    selected_area = st.selectbox("Area", all_areas)

    st.markdown("---")
    st.markdown("### 💰 Cost Parameters (₹)")
    cost_critical = st.number_input("Critical repair", value=1500, step=100)
    cost_high     = st.number_input("High priority",   value=900,  step=50)
    cost_medium   = st.number_input("Medium priority", value=500,  step=50)
    cost_low      = st.number_input("Low priority",    value=250,  step=50)

    st.markdown("---")
    st.markdown("### 👷 Workforce Settings")
    techs_available  = st.slider("Available technicians", 1, 20, 5)
    jobs_per_day     = st.slider("Jobs per technician/day", 1, 10, 4)
    working_hours    = st.slider("Working hours/day", 6, 12, 8)

# ── Data ─────────────────────────────────────────────────────────────────────

df = df_raw.copy()
if selected_area != "All Areas":
    df = df[df["Area"] == selected_area]

# Apply dynamic cost settings
cost_map = {"Critical": cost_critical, "High": cost_high,
            "Medium": cost_medium, "Low": cost_low}
df["Est_Cost_INR"] = df["Priority"].map(cost_map)

faulty_df = df[df["Status"] == "Faulty"].copy()
faulty_df = faulty_df.sort_values(
    "Priority",
    key=lambda x: x.map({"Critical": 0, "High": 1, "Medium": 2, "Low": 3})
)

total_cost  = faulty_df["Est_Cost_INR"].sum()
critical_n  = (faulty_df["Priority"] == "Critical").sum()
high_n      = (faulty_df["Priority"] == "High").sum()
medium_n    = (faulty_df["Priority"] == "Medium").sum()
low_n       = (faulty_df["Priority"] == "Low").sum()
total_jobs  = len(faulty_df)

# Workload estimation
total_capacity   = techs_available * jobs_per_day
days_to_complete = (total_jobs / total_capacity) if total_capacity else 0
completion_date  = (datetime.now() + timedelta(days=days_to_complete)).strftime("%d %b %Y")

# ── Hero ──────────────────────────────────────────────────────────────────────

page_hero(
    "Maintenance Intelligence Center",
    "Priority engine · Cost dashboard · Repair scheduling · Technician workload · Resource planning",
    "🛠️",
)

# ── Alert ─────────────────────────────────────────────────────────────────────

if critical_n > 0:
    alert(f"EMERGENCY — {critical_n} Critical faults detected. Dispatch maintenance crew immediately!", "critical")
elif total_jobs > 0:
    alert(f"{total_jobs} lights require maintenance. Estimated completion by {completion_date}.", "warning")
else:
    alert("All lights are operational. No maintenance required at this time.", "success")

# ── KPI cards ────────────────────────────────────────────────────────────────

section_header("Maintenance Overview", "📋")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(kpi_card("🔧", "Total Repairs", str(total_jobs),
                         "Open work orders", "indigo"), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("💰", "Total Cost Est.", f"₹{total_cost:,}",
                         "Based on current pricing", "orange"), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("📅", "Est. Completion", f"{days_to_complete:.1f} days",
                         f"Target: {completion_date}", "sky"), unsafe_allow_html=True)
with c4:
    st.markdown(kpi_card("👷", "Technicians", str(techs_available),
                         f"{total_capacity} jobs/day capacity", "teal"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Cost breakdown + Priority charts ─────────────────────────────────────────

section_header("Cost & Priority Analysis", "💸")
ch1, ch2 = st.columns(2)

with ch1:
    # Cost by priority
    cost_df = pd.DataFrame({
        "Priority": ["Critical", "High", "Medium", "Low"],
        "Count":    [critical_n, high_n, medium_n, low_n],
        "Unit_Cost":[cost_critical, cost_high, cost_medium, cost_low],
    })
    cost_df["Total_Cost"] = cost_df["Count"] * cost_df["Unit_Cost"]

    fig_cost = go.Figure()
    fig_cost.add_trace(go.Bar(
        x=cost_df["Priority"],
        y=cost_df["Total_Cost"],
        marker_color=[PRIORITY_COLORS.get(p, "#94a3b8") for p in cost_df["Priority"]],
        text=["₹{:,}".format(v) for v in cost_df["Total_Cost"]],
        textposition="outside",
        textfont=dict(color="white"),
        name="Cost (₹)",
    ))
    fig_cost.update_layout(**PLOTLY_LAYOUT, height=320,
                             title="Estimated Cost by Priority",
                             xaxis=dict(showgrid=False),
                             yaxis=dict(gridcolor="rgba(255,255,255,0.06)",
                                        title="Cost (₹)"))
    st.plotly_chart(fig_cost, use_container_width=True)

with ch2:
    # Priority donut
    priority_counts = pd.DataFrame({
        "Priority": ["Critical", "High", "Medium", "Low"],
        "Count":    [critical_n, high_n, medium_n, low_n],
    })
    fig_prio = go.Figure(go.Pie(
        labels=priority_counts["Priority"],
        values=priority_counts["Count"],
        hole=0.6,
        marker_colors=[PRIORITY_COLORS.get(p, "#94a3b8") for p in priority_counts["Priority"]],
        textinfo="label+value+percent",
        textfont=dict(size=12, color="white"),
        pull=[0.06 if p == "Critical" else 0 for p in priority_counts["Priority"]],
    ))
    fig_prio.add_annotation(
        text=f"<b>{total_jobs}</b><br>Jobs",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=18, color="white"),
    )
    fig_prio.update_layout(**PLOTLY_LAYOUT, height=320,
                            title="Maintenance Priority Distribution")
    st.plotly_chart(fig_prio, use_container_width=True)

# ── Area-wise cost heatmap ────────────────────────────────────────────────────

section_header("Area-wise Maintenance Cost Map", "🗺️")

area_cost = (
    faulty_df.groupby("Area")
    .agg(
        Jobs=("Light_ID", "count"),
        Total_Cost=("Est_Cost_INR", "sum"),
        Critical=("Priority", lambda x: (x == "Critical").sum()),
        High=("Priority",     lambda x: (x == "High").sum()),
    )
    .reset_index()
    .sort_values("Total_Cost", ascending=False)
)

if len(area_cost):
    fig_area_cost = px.treemap(
        faulty_df,
        path=["Area", "Priority", "Light_ID"],
        values="Est_Cost_INR",
        color="Priority",
        color_discrete_map=PRIORITY_COLORS,
        title="Cost Treemap — Area → Priority → Light",
    )
    fig_area_cost.update_traces(
        textfont=dict(color="white", size=12),
        marker=dict(line=dict(width=1.5, color="rgba(0,0,0,0.4)")),
    )
    fig_area_cost.update_layout(**PLOTLY_LAYOUT, height=360)
    st.plotly_chart(fig_area_cost, use_container_width=True)
else:
    alert("No faulty lights to display in cost map.", "success")

# ── Technician workload planner ───────────────────────────────────────────────

section_header("Technician Workload Planner", "👷")

wl_left, wl_right = st.columns([2, 1])

with wl_left:
    # Assign jobs to technicians
    if total_jobs > 0:
        tech_names   = [f"Tech-{i+1:02d}" for i in range(techs_available)]
        assignments  = [0] * techs_available
        job_list     = faulty_df["Light_ID"].tolist()

        for i, job in enumerate(job_list):
            assignments[i % techs_available] += 1

        workload_df = pd.DataFrame({
            "Technician": tech_names,
            "Jobs_Assigned": assignments,
            "Est_Hours": [j * (working_hours / jobs_per_day) for j in assignments],
        })

        fig_wl = go.Figure()
        fig_wl.add_trace(go.Bar(
            x=workload_df["Technician"],
            y=workload_df["Jobs_Assigned"],
            marker_color=COLOR_SEQ[:techs_available] if techs_available <= len(COLOR_SEQ) else COLOR_SEQ * 3,
            text=workload_df["Jobs_Assigned"],
            textposition="outside",
            textfont=dict(color="white"),
            name="Jobs",
        ))
        fig_wl.add_hline(
            y=jobs_per_day, line_dash="dash", line_color="#eab308",
            annotation_text=f"Daily Capacity ({jobs_per_day} jobs)",
            annotation_font_color="#fbbf24",
        )
        fig_wl.update_layout(**PLOTLY_LAYOUT, height=300,
                               title="Jobs Assigned per Technician",
                               xaxis=dict(showgrid=False),
                               yaxis=dict(gridcolor="rgba(255,255,255,0.06)"))
        st.plotly_chart(fig_wl, use_container_width=True)
    else:
        alert("No pending jobs to assign.", "success")

with wl_right:
    section_header("Resource Summary", "📦")

    metrics = [
        ("🔧 Open Work Orders",    total_jobs),
        ("👷 Technicians Avail.",  techs_available),
        ("📦 Jobs/Day Capacity",   total_capacity),
        ("📅 Days to Finish",      f"{days_to_complete:.1f}"),
        ("🏁 Target Completion",   completion_date),
        ("💰 Total Budget Est.",   f"₹{total_cost:,}"),
        ("⚡ Avg Cost / Light",    f"₹{int(total_cost/total_jobs) if total_jobs else 0}"),
    ]
    for lbl, val in metrics:
        st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.06);
font-size:0.85rem;color:#e2e8f0;">
  <span style="color:#94a3b8;">{lbl}</span>
  <b style="color:#818cf8;">{val}</b>
</div>""", unsafe_allow_html=True)

# ── Maintenance schedule table ────────────────────────────────────────────────

st.markdown("<br>", unsafe_allow_html=True)
section_header("Maintenance Schedule", "📅")

if len(faulty_df):
    # Add scheduled date based on priority
    priority_sla = {"Critical": 1, "High": 3, "Medium": 7, "Low": 14}
    faulty_df["SLA_Days"] = faulty_df["Priority"].map(priority_sla)
    faulty_df["Scheduled_Date"] = faulty_df["SLA_Days"].apply(
        lambda d: (datetime.now() + timedelta(days=d)).strftime("%d %b %Y")
    )

    display_cols = ["Light_ID", "Area", "Priority", "Action",
                    "Est_Cost_INR", "SLA_Days", "Scheduled_Date", "Voltage", "Current"]
    schedule_display = faulty_df[display_cols].copy()
    schedule_display.rename(columns={
        "Est_Cost_INR":    "Cost (₹)",
        "SLA_Days":        "SLA (Days)",
        "Scheduled_Date":  "Target Date",
    }, inplace=True)

    st.dataframe(
        schedule_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Cost (₹)":   st.column_config.NumberColumn("Cost (₹)", format="₹%d"),
            "SLA (Days)": st.column_config.NumberColumn("SLA (Days)"),
        }
    )

    # Download CSV
    csv = schedule_display.to_csv(index=False)
    st.download_button(
        "⬇️  Export Maintenance Schedule (CSV)",
        data=csv,
        file_name=f"maintenance_schedule_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
else:
    alert("No maintenance required in the selected area.", "success")

# ── Recommendations ───────────────────────────────────────────────────────────

section_header("Maintenance Recommendations", "💡")

r1, r2 = st.columns(2)
with r1:
    recommendation_card("Use a mobile-first field app for technicians to update job status in real time.")
    recommendation_card("Maintain a spare parts inventory of at least 10% of total lights to ensure zero-wait repairs.")
    if critical_n > 0:
        recommendation_card(f"Escalate {critical_n} Critical faults to the Ward Engineer within 2 hours.")
with r2:
    recommendation_card("Group nearby faults into single dispatch routes to reduce travel time and fuel cost by ~30%.")
    recommendation_card("Implement predictive maintenance using IoT sensors to detect faults before total failure.")
    recommendation_card("Track technician close-rate KPI weekly — target: 95% SLA compliance per quarter.")

page_footer()
