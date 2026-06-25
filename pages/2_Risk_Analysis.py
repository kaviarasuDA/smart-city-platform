"""
pages/2_Risk_Analysis.py  ─  SmartCity OS  |  Risk Intelligence
Risk scoring model, critical alerts, predictive failure indicators,
risk trend charts, and smart recommendations engine.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data_utils import load_data, compute_kpis, predict_failure_probability
from utils.styles import (
    inject_global_css, page_hero, section_header, sidebar_brand,
    page_footer, alert, recommendation_card, kpi_card,
    PLOTLY_LAYOUT, COLOR_SEQ, RISK_COLORS,
)

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SmartCity OS · Risk Analysis",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_global_css()

# ── Sidebar ──────────────────────────────────────────────────────────────────

sidebar_brand()
with st.sidebar:
    st.markdown("### ⚙️ Risk Filters")
    df_raw = load_data()
    all_areas = ["All Areas"] + sorted(df_raw["Area"].unique().tolist())
    selected_area = st.selectbox("Area", all_areas)
    risk_filter = st.multiselect(
        "Show Risk Levels",
        ["Critical", "High", "Medium", "Low"],
        default=["Critical", "High", "Medium", "Low"],
    )
    st.markdown("---")
    st.markdown("### ℹ️ Risk Score Formula")
    st.markdown("""
<div style="font-size:0.78rem;color:#94a3b8;line-height:1.7;">
  <b style="color:#818cf8;">Voltage</b><br>
  &lt;160V → +40 pts<br>
  &lt;190V → +25 pts<br>
  &lt;210V → +10 pts<br><br>
  <b style="color:#818cf8;">Current</b><br>
  0A → +40 pts<br>
  &lt;0.2A → +20 pts<br>
  &lt;0.35A → +8 pts<br><br>
  <b style="color:#818cf8;">Status</b><br>
  Faulty → +20 pts<br><br>
  <b style="color:#c084fc;">Score 0-100 · Higher = Worse</b>
</div>""", unsafe_allow_html=True)

# ── Data ─────────────────────────────────────────────────────────────────────

df = df_raw.copy()
if selected_area != "All Areas":
    df = df[df["Area"] == selected_area]
df = df[df["Risk_Level"].isin(risk_filter)]

df["Failure_Prob"] = df.apply(predict_failure_probability, axis=1)
df["Failure_Prob_%"] = (df["Failure_Prob"] * 100).round(1)

kpis = compute_kpis(df_raw if selected_area == "All Areas" else df_raw[df_raw["Area"] == selected_area])

# ── Hero ─────────────────────────────────────────────────────────────────────

page_hero(
    "Risk Intelligence Center",
    "Composite risk scoring · Predictive failure probabilities · Critical alert management · Smart recommendations",
    "🚨",
)

# ── Risk level counts ────────────────────────────────────────────────────────

critical_n = (df["Risk_Level"] == "Critical").sum()
high_n     = (df["Risk_Level"] == "High").sum()
medium_n   = (df["Risk_Level"] == "Medium").sum()
low_n      = (df["Risk_Level"] == "Low").sum()

if critical_n > 0:
    alert(f"CRITICAL ALERT — {critical_n} lights scored Critical risk. Emergency dispatch recommended.", "critical")
elif high_n > 0:
    alert(f"HIGH RISK — {high_n} lights need priority attention within 48 hours.", "warning")
else:
    alert("Risk levels are within manageable range. Continue routine monitoring.", "success")

# ── Risk KPI cards ───────────────────────────────────────────────────────────

section_header("Risk Distribution Summary", "🎯")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(kpi_card("🔴", "Critical Risk", str(critical_n),
                         "Immediate action required", "red"), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("🟠", "High Risk", str(high_n),
                         "Action within 48 hours", "orange"), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("🟡", "Medium Risk", str(medium_n),
                         "Schedule within 2 weeks", "yellow"), unsafe_allow_html=True)
with c4:
    st.markdown(kpi_card("🟢", "Low Risk", str(low_n),
                         "Routine monitoring only", "green"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Risk charts ──────────────────────────────────────────────────────────────

section_header("Risk Visualisation", "📊")
left, right = st.columns(2)

with left:
    risk_counts = df["Risk_Level"].value_counts().reindex(
        ["Critical", "High", "Medium", "Low"], fill_value=0
    ).reset_index()
    risk_counts.columns = ["Risk_Level", "Count"]

    fig_risk_pie = go.Figure(go.Pie(
        labels=risk_counts["Risk_Level"],
        values=risk_counts["Count"],
        hole=0.6,
        marker_colors=[RISK_COLORS.get(r, "#94a3b8") for r in risk_counts["Risk_Level"]],
        textinfo="label+value+percent",
        textfont=dict(size=12, color="white"),
        pull=[0.06 if r == "Critical" else 0 for r in risk_counts["Risk_Level"]],
    ))
    fig_risk_pie.add_annotation(
        text=f"<b>{len(df)}</b><br>Lights",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=18, color="white"),
    )
    fig_risk_pie.update_layout(**PLOTLY_LAYOUT, height=360,
                                title="Risk Level Distribution", showlegend=True)
    st.plotly_chart(fig_risk_pie, use_container_width=True)

with right:
    # Risk score distribution by area – box plot
    area_risk = df_raw.copy()
    if selected_area != "All Areas":
        area_risk = area_risk[area_risk["Area"] == selected_area]

    fig_box = px.box(
        area_risk, x="Area", y="Risk_Score", color="Area",
        color_discrete_sequence=COLOR_SEQ,
        title="Risk Score Distribution by Area",
        points="all",
        hover_data=["Light_ID", "Risk_Level"],
    )
    fig_box.update_layout(**PLOTLY_LAYOUT, height=360, showlegend=False,
                           xaxis=dict(showgrid=False),
                           yaxis=dict(gridcolor="rgba(255,255,255,0.06)",
                                      title="Risk Score (0–100)"))
    st.plotly_chart(fig_box, use_container_width=True)

# ── Area risk stacked bar ─────────────────────────────────────────────────────

section_header("Area-wise Risk Breakdown", "🏙️")

area_risk_grp = (
    df_raw.groupby(["Area", "Risk_Level"])
    .size()
    .reset_index(name="Count")
)
area_risk_grp["Risk_Level"] = pd.Categorical(
    area_risk_grp["Risk_Level"],
    categories=["Critical", "High", "Medium", "Low"],
    ordered=True,
)
area_risk_grp = area_risk_grp.sort_values("Risk_Level")

fig_stacked = px.bar(
    area_risk_grp, x="Area", y="Count", color="Risk_Level",
    color_discrete_map=RISK_COLORS,
    title="Risk Category Breakdown per Area",
    barmode="stack",
    text="Count",
)
fig_stacked.update_traces(textposition="inside", textfont=dict(color="white", size=11))
fig_stacked.update_layout(**PLOTLY_LAYOUT, height=320,
                            xaxis=dict(showgrid=False),
                            yaxis=dict(gridcolor="rgba(255,255,255,0.06)"))
st.plotly_chart(fig_stacked, use_container_width=True)

# ── Predictive failure probability ───────────────────────────────────────────

section_header("Predictive Failure Probability", "🔮")

st.markdown("""
<div class="glass-card" style="font-size:0.85rem;color:#94a3b8;padding:14px 20px;margin-bottom:16px;">
  💡 <b style="color:#e2e8f0;">AI-powered failure probability</b> is estimated using a composite model considering
  light age, supply voltage deviation, operating current anomaly, and current fault status.
  Scores above <b style="color:#f87171;">70%</b> indicate high likelihood of failure within 30 days.
</div>""", unsafe_allow_html=True)

pred_df = df_raw.copy()
if selected_area != "All Areas":
    pred_df = pred_df[pred_df["Area"] == selected_area]
pred_df["Failure_Prob"] = pred_df.apply(predict_failure_probability, axis=1)
pred_df["Failure_Prob_%"] = (pred_df["Failure_Prob"] * 100).round(1)
pred_df = pred_df.sort_values("Failure_Prob_%", ascending=False)

p_left, p_right = st.columns([3, 2])

with p_left:
    fig_pred = go.Figure()
    bar_colors = [
        "#ef4444" if p >= 70 else "#f97316" if p >= 45 else "#eab308" if p >= 25 else "#10b981"
        for p in pred_df["Failure_Prob_%"]
    ]
    fig_pred.add_trace(go.Bar(
        x=pred_df["Light_ID"],
        y=pred_df["Failure_Prob_%"],
        marker_color=bar_colors,
        text=pred_df["Failure_Prob_%"].astype(str) + "%",
        textposition="outside",
        textfont=dict(color="white", size=10),
    ))
    fig_pred.add_hline(y=70, line_dash="dash", line_color="#ef4444",
                        annotation_text="Critical Threshold (70%)",
                        annotation_font_color="#f87171")
    fig_pred.add_hline(y=45, line_dash="dot", line_color="#f97316",
                        annotation_text="High Risk (45%)",
                        annotation_font_color="#fb923c")
    fig_pred.update_layout(**PLOTLY_LAYOUT, height=360,
                             title="Failure Probability per Light",
                             xaxis=dict(showgrid=False),
                             yaxis=dict(range=[0, 110],
                                        gridcolor="rgba(255,255,255,0.06)",
                                        title="Probability (%)"))
    st.plotly_chart(fig_pred, use_container_width=True)

with p_right:
    section_header("Top 5 At-Risk Lights", "⚠️")
    top5 = pred_df.head(5)[["Light_ID", "Area", "Risk_Level", "Failure_Prob_%", "Action"]]
    for _, row in top5.iterrows():
        prob = row["Failure_Prob_%"]
        risk_color = RISK_COLORS.get(row["Risk_Level"], "#94a3b8")
        bar_w = int(prob)
        st.markdown(f"""
<div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
border-radius:12px;padding:14px 16px;margin-bottom:10px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
    <b style="color:white;font-size:0.9rem;">{row['Light_ID']} — {row['Area']}</b>
    <span style="background:{risk_color}33;color:{risk_color};padding:2px 10px;
    border-radius:20px;font-size:0.7rem;font-weight:700;">{row['Risk_Level']}</span>
  </div>
  <div style="background:rgba(255,255,255,0.08);border-radius:6px;height:8px;overflow:hidden;">
    <div style="width:{bar_w}%;height:100%;background:{risk_color};border-radius:6px;"></div>
  </div>
  <div style="margin-top:6px;font-size:0.75rem;color:#94a3b8;">
    Failure prob: <b style="color:{risk_color};">{prob}%</b> &nbsp;·&nbsp; {row['Action']}
  </div>
</div>""", unsafe_allow_html=True)

# ── Voltage-Current risk scatter ─────────────────────────────────────────────

section_header("Risk Score — Voltage & Current Correlation", "📉")

fig_3d = px.scatter(
    pred_df,
    x="Voltage", y="Current",
    color="Risk_Score",
    size="Failure_Prob_%",
    size_max=22,
    color_continuous_scale=[[0, "#10b981"], [0.5, "#eab308"], [1, "#ef4444"]],
    hover_data=["Light_ID", "Area", "Risk_Level", "Failure_Prob_%"],
    title="Risk Landscape: Voltage vs Current (bubble size = failure probability)",
)
fig_3d.add_vline(x=200, line_dash="dash", line_color="#eab308",
                  annotation_text="Low Voltage Threshold",
                  annotation_font_color="#fbbf24")
fig_3d.add_hline(y=0.2, line_dash="dash", line_color="#f97316",
                  annotation_text="Low Current Threshold",
                  annotation_font_color="#fb923c")
fig_3d.update_layout(**PLOTLY_LAYOUT, height=380,
                       xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
                       yaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
                       coloraxis_colorbar=dict(tickfont=dict(color="#e2e8f0"),
                                               title=dict(text="Risk Score", font=dict(color="#e2e8f0"))))
st.plotly_chart(fig_3d, use_container_width=True)

# ── Smart recommendations ─────────────────────────────────────────────────────

section_header("Smart Risk Recommendations", "🤖")

rec_left, rec_right = st.columns(2)

with rec_left:
    st.markdown("**🔴 Immediate Actions**")
    if critical_n > 0:
        recommendation_card(f"Dispatch emergency crew to {critical_n} Critical-risk lights immediately. Do not defer.")
    if (pred_df["Failure_Prob_%"] >= 70).any():
        high_prob_areas = pred_df[pred_df["Failure_Prob_%"] >= 70]["Area"].value_counts().index.tolist()
        recommendation_card(f"High failure probability detected in: {', '.join(high_prob_areas)}. Pre-position spare parts.")
    zero_curr = (pred_df["Current"] == 0).sum()
    if zero_curr:
        recommendation_card(f"{zero_curr} lights have zero current draw — likely open circuit or blown fuse. Inspect wiring.")

with rec_right:
    st.markdown("**🟡 Preventive Actions**")
    if (pred_df["Voltage"] < 210).sum() > 0:
        recommendation_card("Coordinate with power utility to investigate low voltage supply in affected zones.")
    if (pred_df.get("Age_Years", pd.Series([0])) > 7).any():
        recommendation_card("Lights over 7 years old have elevated failure probability. Plan phased bulk replacement.")
    recommendation_card("Install IoT current sensors for real-time anomaly detection to shift from reactive to predictive maintenance.")
    recommendation_card("Create a digital twin of the street-light network for simulation-based failure forecasting.")

# ── Risk table ────────────────────────────────────────────────────────────────

section_header("Complete Risk Register", "📋")

display_cols = ["Light_ID", "Area", "Voltage", "Current", "Status",
                "Risk_Score", "Risk_Level", "Failure_Prob_%", "Action"]
risk_table = pred_df[display_cols].copy()

st.dataframe(
    risk_table,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Risk_Score":      st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=100),
        "Failure_Prob_%":  st.column_config.ProgressColumn("Failure Prob %", min_value=0, max_value=100),
        "Risk_Level":      st.column_config.TextColumn("Risk Level"),
    }
)

page_footer()
