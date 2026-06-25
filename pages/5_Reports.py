"""
pages/5_Reports.py  ─  SmartCity OS  |  Professional Reports
CSV exports, PDF report generation, analytics summary,
maintenance report, fault report, and executive summary.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data_utils import load_data, compute_kpis, area_ranking, predict_failure_probability
from utils.styles import (
    inject_global_css, page_hero, section_header, sidebar_brand,
    page_footer, alert, recommendation_card, kpi_card,
    PLOTLY_LAYOUT, STATUS_COLORS, RISK_COLORS, PRIORITY_COLORS,
)

# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SmartCity OS · Reports",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_global_css()

# ── Sidebar ────────────────────────────────────────────────────────────────────

sidebar_brand()
with st.sidebar:
    st.markdown("### 📄 Report Settings")
    df_raw = load_data()
    all_areas = ["All Areas"] + sorted(df_raw["Area"].unique().tolist())
    selected_area = st.selectbox("Area Scope", all_areas)
    report_date   = st.date_input("Report Date", value=datetime.now().date())

    st.markdown("---")
    st.markdown("### 🖨️ Export Sections")
    inc_summary   = st.checkbox("Executive Summary",      value=True)
    inc_fault     = st.checkbox("Fault Report",           value=True)
    inc_risk      = st.checkbox("Risk Register",          value=True)
    inc_maint     = st.checkbox("Maintenance Schedule",   value=True)
    inc_area      = st.checkbox("Area Performance Table", value=True)

# ── Data ──────────────────────────────────────────────────────────────────────

df = df_raw.copy()
if selected_area != "All Areas":
    df = df[df["Area"] == selected_area]

df["Failure_Prob_%"] = df.apply(predict_failure_probability, axis=1) * 100

kpis = compute_kpis(df)
rank_df = area_ranking(df)
faulty_df = df[df["Status"] == "Faulty"].copy()
priority_sla = {"Critical": 1, "High": 3, "Medium": 7, "Low": 14}
if len(faulty_df):
    from datetime import timedelta
    faulty_df["SLA_Days"]       = faulty_df["Priority"].map(priority_sla)
    faulty_df["Scheduled_Date"] = faulty_df["SLA_Days"].apply(
        lambda d: (datetime.now() + timedelta(days=d)).strftime("%d %b %Y")
    )

scope_label = selected_area if selected_area != "All Areas" else "All Areas"
rpt_ts      = report_date.strftime("%d %B %Y")

# ── Hero ──────────────────────────────────────────────────────────────────────

page_hero(
    "Reports & Export Center",
    f"Generate, preview, and download professional reports · Scope: {scope_label} · Date: {rpt_ts}",
    "📄",
)

# ── Report type tabs ──────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive Summary",
    "🚨 Fault Report",
    "🛠️ Maintenance Report",
    "📋 Full Data Export",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 – EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

with tab1:
    section_header("Executive Summary Report", "📊")

    # Summary header card
    st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(139,92,246,0.15));
border:1px solid rgba(99,102,241,0.3);border-radius:16px;padding:24px 28px;color:white;
margin-bottom:20px;">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
    <div>
      <h2 style="margin:0 0 6px;font-size:1.4rem;color:#c7d2fe;">
        🏙️ SmartCity OS — Street Light Analytics Report
      </h2>
      <p style="margin:0;color:#94a3b8;font-size:0.9rem;">
        Area: <b style="color:#e2e8f0;">{scope_label}</b> &nbsp;|&nbsp;
        Generated: <b style="color:#e2e8f0;">{rpt_ts}</b> &nbsp;|&nbsp;
        Platform: <b style="color:#e2e8f0;">SmartCity OS v3.0</b>
      </p>
    </div>
    <div style="text-align:right;font-size:0.75rem;color:#64748b;">
      Confidential — Municipal Use Only
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    # KPI grid
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("🚦", "Total Lights",    str(kpis["total"]),   "", "indigo"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("✅", "Working",         str(kpis["working"]), "", "green"),  unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("❌", "Faulty",          str(kpis["faulty"]),  "", "red"),    unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("💚", "Health Score",    f"{kpis['health_score']}%", "", "teal"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown(kpi_card("📈", "Fault Rate",      f"{kpis['fault_pct']}%", "",   "orange"), unsafe_allow_html=True)
    with c6:
        st.markdown(kpi_card("⚡", "Avg Voltage",     f"{kpis['avg_voltage']} V", "", "sky"),   unsafe_allow_html=True)
    with c7:
        st.markdown(kpi_card("🔋", "Avg Current",     f"{kpis['avg_current']} A", "", "purple"), unsafe_allow_html=True)
    with c8:
        st.markdown(kpi_card("💰", "Maint. Cost",     f"₹{kpis['total_cost']:,}", "", "pink"),  unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts
    ch1, ch2 = st.columns(2)
    with ch1:
        counts = df["Status"].value_counts().reset_index()
        counts.columns = ["Status", "Count"]
        fig = px.pie(counts, names="Status", values="Count",
                     color="Status", color_discrete_map=STATUS_COLORS,
                     hole=0.55, title="Status Distribution")
        fig.update_layout(**PLOTLY_LAYOUT, height=300)
        st.plotly_chart(fig, use_container_width=True)
    with ch2:
        rc = df["Risk_Level"].value_counts().reindex(
            ["Critical", "High", "Medium", "Low"], fill_value=0
        ).reset_index()
        rc.columns = ["Risk", "Count"]
        fig2 = px.bar(rc, x="Risk", y="Count",
                      color="Risk", color_discrete_map=RISK_COLORS,
                      title="Risk Level Distribution", text="Count")
        fig2.update_traces(textposition="outside", textfont=dict(color="white"))
        fig2.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=False,
                            xaxis=dict(showgrid=False),
                            yaxis=dict(gridcolor="rgba(255,255,255,0.06)"))
        st.plotly_chart(fig2, use_container_width=True)

    # Area ranking table
    section_header("Area Performance Ranking", "🏆")
    st.dataframe(rank_df[[
        "Rank", "Area", "Total", "Working", "Faulty", "Fault_Rate_%", "Health_%"
    ]], use_container_width=True, hide_index=True,
        column_config={
            "Health_%":     st.column_config.ProgressColumn("Health %", min_value=0, max_value=100),
            "Fault_Rate_%": st.column_config.NumberColumn("Fault Rate %", format="%.1f%%"),
        })

    # Insights
    section_header("Executive Insights", "🧠")
    insights_text = []
    if kpis["fault_pct"] > 30:
        insights_text.append(f"⚠️ Fault rate of **{kpis['fault_pct']}%** exceeds critical threshold. Emergency response required.")
    elif kpis["fault_pct"] > 15:
        insights_text.append(f"🟡 Fault rate of **{kpis['fault_pct']}%** is above advisory level. Proactive maintenance advised.")
    else:
        insights_text.append(f"✅ Fault rate at **{kpis['fault_pct']}%** — within acceptable operational limits.")
    insights_text.append(f"🏙️ **{kpis['top_area']}** zone is the highest-impact area with **{kpis['top_area_cnt']}** faults.")
    insights_text.append(f"💰 Estimated maintenance expenditure: **₹{kpis['total_cost']:,}** across {kpis['faulty']} faulty units.")
    if kpis["critical_cnt"] > 0:
        insights_text.append(f"🚨 **{kpis['critical_cnt']}** lights are in Critical condition — immediate dispatch recommended.")

    for i in insights_text:
        st.markdown(f"""
<div class="glass-card" style="padding:12px 18px;margin-bottom:8px;font-size:0.88rem;">{i}</div>""",
        unsafe_allow_html=True)

    # Export summary CSV
    summary_data = {
        "Metric": ["Total Lights", "Working", "Faulty", "Fault %",
                   "Health Score", "Avg Voltage", "Avg Current", "Maint. Cost (INR)",
                   "Critical Alerts", "Top Fault Area"],
        "Value":  [kpis["total"], kpis["working"], kpis["faulty"],
                   f"{kpis['fault_pct']}%", f"{kpis['health_score']}%",
                   f"{kpis['avg_voltage']} V", f"{kpis['avg_current']} A",
                   f"₹{kpis['total_cost']:,}", kpis["critical_cnt"], kpis["top_area"]],
    }
    summary_df = pd.DataFrame(summary_data)
    csv_summary = summary_df.to_csv(index=False)
    st.download_button(
        "⬇️  Download Executive Summary (CSV)",
        data=csv_summary,
        file_name=f"executive_summary_{report_date}.csv",
        mime="text/csv",
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 – FAULT REPORT
# ══════════════════════════════════════════════════════════════════════════════

with tab2:
    section_header("Fault Report", "🚨")

    if kpis["faulty"] == 0:
        alert("No faulty lights in the selected scope. System is fully operational.", "success")
    else:
        alert(f"{kpis['faulty']} faulty lights detected. Report generated for {rpt_ts}.", "warning")

        # Fault by area chart
        fba = df[df["Status"] == "Faulty"].groupby("Area").size().reset_index(name="Faults")
        fig_fba = px.bar(
            fba.sort_values("Faults", ascending=True),
            x="Faults", y="Area", orientation="h",
            color="Faults",
            color_continuous_scale=["#eab308", "#f97316", "#ef4444"],
            title="Faulty Lights by Area",
            text="Faults",
        )
        fig_fba.update_traces(textposition="outside", textfont=dict(color="white"))
        fig_fba.update_layout(**PLOTLY_LAYOUT, height=280,
                               coloraxis_showscale=False,
                               xaxis=dict(showgrid=False),
                               yaxis=dict(showgrid=False))
        st.plotly_chart(fig_fba, use_container_width=True)

        # Faulty table
        fault_cols = ["Light_ID", "Area", "Voltage", "Current", "Status",
                      "Risk_Level", "Risk_Score", "Priority", "Action", "Failure_Prob_%"]
        fault_report_df = df[df["Status"] == "Faulty"][fault_cols].copy()
        fault_report_df = fault_report_df.sort_values("Risk_Score", ascending=False)

        st.dataframe(
            fault_report_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Risk_Score":     st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=100),
                "Failure_Prob_%": st.column_config.ProgressColumn("Failure Prob %", min_value=0, max_value=100),
            }
        )

        csv_fault = fault_report_df.to_csv(index=False)
        st.download_button(
            "⬇️  Download Fault Report (CSV)",
            data=csv_fault,
            file_name=f"fault_report_{report_date}.csv",
            mime="text/csv",
        )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 – MAINTENANCE REPORT
# ══════════════════════════════════════════════════════════════════════════════

with tab3:
    section_header("Maintenance Schedule Report", "🛠️")

    if len(faulty_df) == 0:
        alert("No maintenance required in the current scope.", "success")
    else:
        total_cost = faulty_df["Est_Cost_INR"].sum()
        st.markdown(f"""
<div class="glass-card" style="margin-bottom:16px;">
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;text-align:center;">
    <div><div style="font-size:1.6rem;font-weight:800;color:#818cf8;">{len(faulty_df)}</div>
         <div style="font-size:0.72rem;color:#94a3b8;text-transform:uppercase;">Total Jobs</div></div>
    <div><div style="font-size:1.6rem;font-weight:800;color:#f87171;">
          {(faulty_df["Priority"]=="Critical").sum()}</div>
         <div style="font-size:0.72rem;color:#94a3b8;text-transform:uppercase;">Critical</div></div>
    <div><div style="font-size:1.6rem;font-weight:800;color:#fb923c;">
          {(faulty_df["Priority"]=="High").sum()}</div>
         <div style="font-size:0.72rem;color:#94a3b8;text-transform:uppercase;">High Priority</div></div>
    <div><div style="font-size:1.6rem;font-weight:800;color:#34d399;">₹{total_cost:,}</div>
         <div style="font-size:0.72rem;color:#94a3b8;text-transform:uppercase;">Total Cost Est.</div></div>
  </div>
</div>""", unsafe_allow_html=True)

        maint_cols = ["Light_ID", "Area", "Priority", "Action",
                      "Est_Cost_INR", "Scheduled_Date", "Voltage", "Current"]
        maint_display = faulty_df[maint_cols].copy()
        maint_display = maint_display.sort_values(
            "Priority",
            key=lambda x: x.map({"Critical": 0, "High": 1, "Medium": 2, "Low": 3})
        )
        maint_display.rename(columns={"Est_Cost_INR": "Cost (₹)"}, inplace=True)

        st.dataframe(
            maint_display,
            use_container_width=True,
            hide_index=True,
            column_config={"Cost (₹)": st.column_config.NumberColumn("Cost (₹)", format="₹%d")}
        )

        csv_maint = maint_display.to_csv(index=False)
        st.download_button(
            "⬇️  Download Maintenance Report (CSV)",
            data=csv_maint,
            file_name=f"maintenance_report_{report_date}.csv",
            mime="text/csv",
        )

        section_header("Cost Summary by Priority", "💰")
        cost_grp = (
            faulty_df.groupby("Priority")["Est_Cost_INR"]
            .agg(["count", "sum"])
            .reset_index()
            .rename(columns={"count": "Jobs", "sum": "Total_Cost (₹)"})
        )
        cost_grp["Avg_Cost (₹)"] = (cost_grp["Total_Cost (₹)"] / cost_grp["Jobs"]).astype(int)
        st.dataframe(cost_grp, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 – FULL DATA EXPORT
# ══════════════════════════════════════════════════════════════════════════════

with tab4:
    section_header("Full Dataset Export", "📋")

    export_df = df.copy()

    # Column selector
    all_cols = export_df.columns.tolist()
    selected_cols = st.multiselect(
        "Select columns to export",
        all_cols,
        default=all_cols,
    )

    if selected_cols:
        preview_df = export_df[selected_cols]

        st.markdown(f"""
<div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);
border-radius:10px;padding:12px 20px;color:#94a3b8;font-size:0.82rem;margin-bottom:12px;">
  📊 Preview: <b style="color:#e2e8f0;">{len(preview_df)} rows × {len(selected_cols)} columns</b>
  &nbsp;|&nbsp; Scope: <b style="color:#818cf8;">{scope_label}</b>
  &nbsp;|&nbsp; Generated: <b style="color:#818cf8;">{rpt_ts}</b>
</div>""", unsafe_allow_html=True)

        st.dataframe(preview_df, use_container_width=True, hide_index=True)

        # Export buttons
        dl1, dl2 = st.columns(2)
        with dl1:
            csv_all = preview_df.to_csv(index=False)
            st.download_button(
                "⬇️  Download Full Dataset (CSV)",
                data=csv_all,
                file_name=f"smartcity_streetlights_{scope_label}_{report_date}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with dl2:
            # Excel export via openpyxl
            try:
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    preview_df.to_excel(writer, sheet_name="Street Lights", index=False)
                    if len(faulty_df):
                        faulty_df[selected_cols if all(c in faulty_df.columns for c in selected_cols) else faulty_df.columns]\
                            .to_excel(writer, sheet_name="Faulty Lights", index=False)
                    rank_df.to_excel(writer, sheet_name="Area Ranking", index=False)
                excel_data = output.getvalue()
                st.download_button(
                    "⬇️  Download Full Report (Excel)",
                    data=excel_data,
                    file_name=f"smartcity_report_{scope_label}_{report_date}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            except Exception as e:
                st.info(f"Excel export requires openpyxl: `pip install openpyxl` ({e})")

    # Bulk download — all reports as separate CSVs info
    section_header("Bulk Download Checklist", "📦")
    st.markdown("""
<div class="glass-card" style="font-size:0.88rem;color:#94a3b8;line-height:2;">
  Download individual reports from each tab above, or use the buttons below for the full combined export.
  <br><br>
  ✅ Executive Summary CSV &nbsp;→&nbsp; Tab 1<br>
  ✅ Fault Report CSV &nbsp;→&nbsp; Tab 2<br>
  ✅ Maintenance Schedule CSV &nbsp;→&nbsp; Tab 3<br>
  ✅ Full Dataset CSV / Excel &nbsp;→&nbsp; This tab<br><br>
  💡 <b style="color:#e2e8f0;">Pro Tip:</b> Use Excel export for a multi-sheet workbook containing
  all three reports in one file — ideal for sharing with ward officers and supervisors.
</div>""", unsafe_allow_html=True)

page_footer()
