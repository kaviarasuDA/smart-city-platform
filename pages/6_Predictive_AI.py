"""
pages/6_Predictive_AI.py  ─  SmartCity OS  |  Predictive AI
Predictive maintenance, fault forecasting, AI-based recommendations,
smart city insights, and decision support analytics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data_utils import load_data, compute_kpis, predict_failure_probability
from utils.styles import (
    inject_global_css, page_hero, section_header, sidebar_brand,
    page_footer, alert, recommendation_card, kpi_card,
    PLOTLY_LAYOUT, COLOR_SEQ, RISK_COLORS,
)

# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SmartCity OS · Predictive AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_global_css()

# ── Sidebar ────────────────────────────────────────────────────────────────────

sidebar_brand()
with st.sidebar:
    st.markdown("### 🤖 AI Model Settings")
    df_raw = load_data()
    all_areas = ["All Areas"] + sorted(df_raw["Area"].unique().tolist())
    selected_area = st.selectbox("Area Scope", all_areas)

    st.markdown("---")
    st.markdown("### 🔮 Forecast Settings")
    forecast_days = st.slider("Forecast Horizon (days)", 7, 90, 30)
    risk_threshold = st.slider("Alert Threshold (%)", 30, 90, 60)

    st.markdown("---")
    st.markdown("""
<div style="font-size:0.78rem;color:#64748b;line-height:1.7;">
  <b style="color:#818cf8;">AI Model Components:</b><br>
  • Voltage deviation analysis<br>
  • Current anomaly detection<br>
  • Age-based degradation model<br>
  • Multi-factor risk scoring<br>
  • Heuristic failure forecasting<br><br>
  <span style="color:#6366f1;">Built on Python + Pandas</span>
</div>""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────

df = df_raw.copy()
if selected_area != "All Areas":
    df = df[df["Area"] == selected_area]

df["Failure_Prob"]   = df.apply(predict_failure_probability, axis=1)
df["Failure_Prob_%"] = (df["Failure_Prob"] * 100).round(1)

kpis = compute_kpis(df)
n_at_risk = (df["Failure_Prob_%"] >= risk_threshold).sum()

# ── Hero ──────────────────────────────────────────────────────────────────────

page_hero(
    "Predictive AI & Smart City Intelligence",
    "Fault forecasting · Failure probability engine · AI recommendations · Decision support analytics",
    "🤖",
)

# ── AI Status banner ──────────────────────────────────────────────────────────

st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(99,102,241,0.2),rgba(139,92,246,0.2));
border:1px solid rgba(99,102,241,0.35);border-radius:14px;padding:16px 22px;
color:white;margin-bottom:20px;display:flex;align-items:center;gap:16px;">
  <div style="font-size:2.5rem;">🤖</div>
  <div>
    <b style="font-size:1rem;color:#c7d2fe;">Predictive Maintenance Engine — Active</b><br>
    <span style="font-size:0.82rem;color:#94a3b8;">
      Analysing {len(df)} lights · {forecast_days}-day forecast horizon ·
      Alert threshold: {risk_threshold}% · <b style="color:#f87171;">{n_at_risk} lights above threshold</b>
    </span>
  </div>
</div>""", unsafe_allow_html=True)

# ── KPI Strip ─────────────────────────────────────────────────────────────────

c1, c2, c3, c4 = st.columns(4)
high_prob = (df["Failure_Prob_%"] >= 70).sum()
med_prob  = ((df["Failure_Prob_%"] >= 45) & (df["Failure_Prob_%"] < 70)).sum()
avg_prob  = df["Failure_Prob_%"].mean()

with c1:
    st.markdown(kpi_card("🔮", "Avg Failure Prob.", f"{avg_prob:.1f}%",
                         "Network-wide average", "purple"), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("🔴", "High Failure Risk", str(high_prob),
                         "Probability ≥ 70%", "red"), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("🟠", "Medium Failure Risk", str(med_prob),
                         "Probability 45–70%", "orange"), unsafe_allow_html=True)
with c4:
    st.markdown(kpi_card("📅", "Forecast Horizon", f"{forecast_days}d",
                         f"Predicting until {(datetime.now()+timedelta(days=forecast_days)).strftime('%d %b')}", "sky"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1 – Failure Probability Rankings
# ═══════════════════════════════════════════════════════════════════════════

section_header("Failure Probability Ranking", "🎯")

prob_df = df.sort_values("Failure_Prob_%", ascending=False).copy()

p_left, p_right = st.columns([3, 2])

with p_left:
    bar_colors = [
        "#ef4444" if p >= 70 else "#f97316" if p >= 45 else "#eab308" if p >= 25 else "#10b981"
        for p in prob_df["Failure_Prob_%"]
    ]

    fig_prob = go.Figure(go.Bar(
        x=prob_df["Light_ID"],
        y=prob_df["Failure_Prob_%"],
        marker_color=bar_colors,
        text=prob_df["Failure_Prob_%"].astype(str) + "%",
        textposition="outside",
        textfont=dict(color="white", size=9),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Failure Probability: %{y:.1f}%<br>"
            "<extra></extra>"
        ),
    ))
    fig_prob.add_hline(y=risk_threshold, line_dash="dash", line_color="#ef4444",
                        annotation_text=f"Alert Threshold ({risk_threshold}%)",
                        annotation_font_color="#f87171")
    fig_prob.update_layout(**PLOTLY_LAYOUT, height=380,
                            title="Predicted 30-Day Failure Probability per Light",
                            xaxis=dict(showgrid=False),
                            yaxis=dict(range=[0, 110],
                                       gridcolor="rgba(255,255,255,0.06)",
                                       title="Probability (%)"))
    st.plotly_chart(fig_prob, use_container_width=True)

with p_right:
    section_header("Priority Watch List", "⚠️")
    watch_list = prob_df[prob_df["Failure_Prob_%"] >= risk_threshold][
        ["Light_ID", "Area", "Risk_Level", "Failure_Prob_%"]
    ].head(8)

    if len(watch_list):
        for _, row in watch_list.iterrows():
            prob  = row["Failure_Prob_%"]
            color = RISK_COLORS.get(row["Risk_Level"], "#94a3b8")
            bar_w = int(min(prob, 100))
            st.markdown(f"""
<div style="background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.18);
border-radius:10px;padding:12px 14px;margin-bottom:8px;">
  <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
    <b style="color:white;font-size:0.85rem;">{row['Light_ID']} — {row['Area']}</b>
    <span style="color:{color};font-size:0.8rem;font-weight:700;">{prob}%</span>
  </div>
  <div style="background:rgba(255,255,255,0.08);border-radius:4px;height:6px;">
    <div style="width:{bar_w}%;height:100%;background:{color};border-radius:4px;"></div>
  </div>
  <div style="margin-top:4px;font-size:0.72rem;color:#94a3b8;">{row['Risk_Level']} Risk</div>
</div>""", unsafe_allow_html=True)
    else:
        alert(f"No lights above {risk_threshold}% failure probability threshold.", "success")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2 – Simulated Fault Forecast Trend
# ═══════════════════════════════════════════════════════════════════════════

section_header(f"Fault Forecast — Next {forecast_days} Days", "📈")

st.markdown("""
<div class="glass-card" style="font-size:0.83rem;color:#94a3b8;padding:12px 18px;margin-bottom:14px;">
  ⚠️ <b style="color:#e2e8f0;">Simulation Mode:</b> The forecast below is generated using a
  heuristic degradation model based on current voltage deviation, current anomaly, and light age.
  In a production deployment, this would be replaced by an ML time-series model (LSTM / Prophet).
</div>""", unsafe_allow_html=True)

# Generate simulated forecast
np.random.seed(42)
dates         = [datetime.now().date() + timedelta(days=i) for i in range(forecast_days)]
base_faults   = kpis["faulty"]
trend         = np.linspace(0, base_faults * 0.4, forecast_days)
noise         = np.random.normal(0, 0.5, forecast_days)
predicted     = np.clip(base_faults + trend + noise, 0, kpis["total"]).astype(int)
upper_band    = np.clip(predicted + np.random.randint(1, 3, forecast_days), 0, kpis["total"])
lower_band    = np.clip(predicted - np.random.randint(0, 2, forecast_days), 0, kpis["total"])

forecast_df = pd.DataFrame({
    "Date": dates,
    "Predicted_Faults": predicted,
    "Upper": upper_band,
    "Lower": lower_band,
})
forecast_df["Date_str"] = forecast_df["Date"].astype(str)

fig_forecast = go.Figure()

# Confidence band
fig_forecast.add_trace(go.Scatter(
    x=forecast_df["Date_str"].tolist() + forecast_df["Date_str"].tolist()[::-1],
    y=forecast_df["Upper"].tolist() + forecast_df["Lower"].tolist()[::-1],
    fill="toself",
    fillcolor="rgba(99,102,241,0.1)",
    line=dict(color="rgba(255,255,255,0)"),
    name="Confidence Band",
    showlegend=True,
))

# Predicted line
fig_forecast.add_trace(go.Scatter(
    x=forecast_df["Date_str"],
    y=forecast_df["Predicted_Faults"],
    mode="lines+markers",
    line=dict(color="#6366f1", width=2.5),
    marker=dict(size=5, color="#818cf8"),
    name="Predicted Faults",
))

# Today marker
fig_forecast.add_vline(
    x=str(datetime.now().date()),
    line_dash="dash", line_color="#eab308",
    annotation_text="Today",
    annotation_font_color="#fbbf24",
)

fig_forecast.update_layout(**PLOTLY_LAYOUT, height=360,
                             title=f"Predicted Fault Count — {forecast_days}-Day Horizon",
                             xaxis=dict(showgrid=False, tickangle=-30),
                             yaxis=dict(gridcolor="rgba(255,255,255,0.06)",
                                        title="Estimated Fault Count"))
st.plotly_chart(fig_forecast, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3 – Age vs Failure Probability
# ═══════════════════════════════════════════════════════════════════════════

section_header("Degradation Analysis — Age vs Failure Probability", "📉")

a_left, a_right = st.columns(2)

with a_left:
    fig_age = px.scatter(
        df, x="Age_Years", y="Failure_Prob_%",
        color="Risk_Level",
        color_discrete_map=RISK_COLORS,
        size="Risk_Score",
        size_max=18,
        hover_data=["Light_ID", "Area", "Status"],
        title="Age vs Failure Probability",
        trendline="ols",
        trendline_color_override="#c084fc",
    )
    fig_age.update_layout(**PLOTLY_LAYOUT, height=340,
                           xaxis=dict(showgrid=False, title="Light Age (Years)"),
                           yaxis=dict(gridcolor="rgba(255,255,255,0.06)",
                                      title="Failure Probability (%)"))
    st.plotly_chart(fig_age, use_container_width=True)

with a_right:
    # Age distribution histogram
    fig_age_hist = px.histogram(
        df, x="Age_Years", color="Status",
        color_discrete_map={"Working": "#10b981", "Faulty": "#ef4444"},
        nbins=8, title="Age Distribution by Status",
        barmode="overlay", opacity=0.8,
    )
    fig_age_hist.update_layout(**PLOTLY_LAYOUT, height=340,
                                xaxis=dict(showgrid=False, title="Age (Years)"),
                                yaxis=dict(gridcolor="rgba(255,255,255,0.06)",
                                           title="Count"))
    st.plotly_chart(fig_age_hist, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4 – Smart City Decision Support
# ═══════════════════════════════════════════════════════════════════════════

section_header("Smart City Decision Support", "🏙️")

d_left, d_right = st.columns(2)

with d_left:
    st.markdown("**📊 Operational Decisions**")

    decisions = []
    if kpis["fault_pct"] > 30:
        decisions.append(("🔴 CRITICAL", "Activate Emergency Maintenance Protocol. Escalate to City Engineer.", "#ef4444"))
    elif kpis["fault_pct"] > 15:
        decisions.append(("🟡 ACTION NEEDED", "Increase inspection frequency. Pre-order spare parts.", "#eab308"))
    else:
        decisions.append(("🟢 NORMAL OPS", "Continue routine monitoring cycle. Monthly inspection schedule.", "#10b981"))

    if kpis["avg_voltage"] < 215:
        decisions.append(("⚡ POWER ISSUE", f"Average voltage {kpis['avg_voltage']}V is below norm. Contact power utility.", "#f97316"))

    if high_prob > 0:
        decisions.append(("🔮 PREDICTIVE", f"{high_prob} lights forecast to fail within 30 days. Pre-schedule replacements.", "#8b5cf6"))

    if kpis["critical_cnt"] > 0:
        decisions.append(("🚨 ALERT", f"{kpis['critical_cnt']} critical-risk units require same-day dispatch.", "#ef4444"))

    for label, text, color in decisions:
        st.markdown(f"""
<div style="background:{color}15;border:1px solid {color}40;border-left:4px solid {color};
border-radius:10px;padding:14px 16px;margin-bottom:10px;color:#e2e8f0;">
  <div style="font-size:0.72rem;font-weight:700;color:{color};letter-spacing:0.08em;margin-bottom:4px;">
    {label}
  </div>
  <div style="font-size:0.87rem;">{text}</div>
</div>""", unsafe_allow_html=True)

with d_right:
    st.markdown("**🤖 AI-Generated Recommendations**")
    recs = [
        "Deploy a real-time IoT monitoring layer using NB-IoT or LoRaWAN sensors on all street lights to enable true predictive maintenance.",
        f"Schedule bulk replacement of {high_prob} lights with ≥70% failure probability before monsoon season to avoid emergency callouts.",
        "Integrate this platform with the city's GIS dashboard for unified urban infrastructure management.",
        f"Optimise technician routes for {kpis['top_area']} zone (highest fault density) using Google Maps API routing to cut travel time by ~35%.",
        "Implement dynamic lighting (dimming during off-peak hours) to extend LED lifespan by up to 25% and reduce energy consumption.",
        "Set up automated WhatsApp/SMS alerts to ward supervisors when Critical faults are detected.",
    ]
    for rec in recs:
        recommendation_card(rec)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5 – Smart City KPI Scorecard
# ═══════════════════════════════════════════════════════════════════════════

section_header("Smart City KPI Scorecard", "🏅")

scorecard_data = {
    "KPI":          ["Network Uptime", "Fault Response Rate", "Predictive Coverage",
                     "Energy Efficiency", "Cost Optimisation", "Citizen Satisfaction"],
    "Target":       ["99%",     "< 24h",  "≥ 80%",  "LED ≥ 90%",  "≤ ₹800/unit",  "≥ 4.0/5.0"],
    "Current":      [f"{kpis['health_score']}%",
                     "48h avg",
                     f"{min(100-kpis['fault_pct'], 100):.0f}%",
                     "78% LED",
                     f"₹{int(kpis['total_cost']/max(kpis['faulty'],1))}",
                     "3.8/5.0"],
    "Status":       ["✅" if kpis["health_score"] >= 90 else "⚠️",
                     "⚠️", "✅" if kpis["fault_pct"] < 20 else "❌",
                     "⚠️", "✅", "⚠️"],
    "Trend":        ["↑ Improving", "→ Stable", "↑ Improving", "↑ Improving", "↓ Worsening", "→ Stable"],
}
scorecard_df = pd.DataFrame(scorecard_data)
st.dataframe(scorecard_df, use_container_width=True, hide_index=True)

# ── Full prediction table ─────────────────────────────────────────────────────

with st.expander("🔍 Full Predictive Analysis Table"):
    pred_table = prob_df[[
        "Light_ID", "Area", "Voltage", "Current", "Status", "Age_Years",
        "Risk_Level", "Risk_Score", "Failure_Prob_%", "Priority", "Action"
    ]].copy()
    st.dataframe(
        pred_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Risk_Score":     st.column_config.ProgressColumn("Risk Score",    min_value=0, max_value=100),
            "Failure_Prob_%": st.column_config.ProgressColumn("Failure Prob %",min_value=0, max_value=100),
        }
    )
    csv = pred_table.to_csv(index=False)
    st.download_button(
        "⬇️  Download Predictive Analysis (CSV)",
        data=csv,
        file_name=f"predictive_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

page_footer()
