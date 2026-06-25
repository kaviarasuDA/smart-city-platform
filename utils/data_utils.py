"""
utils/data_utils.py
Shared data loading, KPI computation, risk scoring, and styling helpers.
"""

import pandas as pd
import numpy as np
from datetime import datetime, date


# ─────────────────────────────────────────────
#  DATA LOADING
# ─────────────────────────────────────────────

def load_data(path: str = "data/street_lights.csv") -> pd.DataFrame:
    """Load and enrich the street-light dataset."""
    df = pd.read_csv(path)

    # Derived columns
    df["Risk_Score"]  = df.apply(_compute_risk_score, axis=1)
    df["Risk_Level"]  = df["Risk_Score"].apply(_risk_label)
    df["Priority"]    = df.apply(_maintenance_priority, axis=1)
    df["Action"]      = df["Priority"].map({
        "Critical": "Emergency Replacement",
        "High":     "Replace Bulb/Ballast",
        "Medium":   "Check Wiring & Connections",
        "Low":      "Schedule Routine Inspection",
    })
    df["Est_Cost_INR"] = df["Priority"].map({
        "Critical": 1500,
        "High":     900,
        "Medium":   500,
        "Low":      250,
    })
    df["Health_Score"] = df.apply(_light_health_score, axis=1)

    # Age from Install_Year if column exists
    if "Install_Year" in df.columns:
        df["Age_Years"] = datetime.now().year - df["Install_Year"]
    else:
        df["Age_Years"] = 5   # default

    return df


# ─────────────────────────────────────────────
#  SCORING HELPERS  (private)
# ─────────────────────────────────────────────

def _compute_risk_score(row) -> int:
    """0-100 composite risk score (higher = worse)."""
    score = 0

    # Voltage risk
    if row["Voltage"] < 160:
        score += 40
    elif row["Voltage"] < 190:
        score += 25
    elif row["Voltage"] < 210:
        score += 10

    # Current risk
    if row["Current"] == 0:
        score += 40
    elif row["Current"] < 0.2:
        score += 20
    elif row["Current"] < 0.35:
        score += 8

    # Status
    if row["Status"] == "Faulty":
        score += 20

    return min(score, 100)


def _risk_label(score: int) -> str:
    if score >= 70:
        return "Critical"
    elif score >= 45:
        return "High"
    elif score >= 20:
        return "Medium"
    return "Low"


def _maintenance_priority(row) -> str:
    if row["Current"] == 0 and row["Voltage"] < 180:
        return "Critical"
    elif row["Current"] == 0:
        return "High"
    elif row["Voltage"] < 200:
        return "Medium"
    return "Low"


def _light_health_score(row) -> float:
    """0-100 individual health score (higher = healthier)."""
    score = 100.0
    if row["Status"] == "Faulty":
        score -= 50
    if row["Voltage"] < 200:
        score -= 20
    elif row["Voltage"] < 215:
        score -= 8
    if row["Current"] < 0.1:
        score -= 20
    elif row["Current"] < 0.3:
        score -= 8
    return max(score, 0)


# ─────────────────────────────────────────────
#  KPI SUMMARY
# ─────────────────────────────────────────────

def compute_kpis(df: pd.DataFrame) -> dict:
    total   = len(df)
    working = (df["Status"] == "Working").sum()
    faulty  = (df["Status"] == "Faulty").sum()

    fault_pct    = faulty / total * 100 if total else 0
    health_score = working / total * 100 if total else 0
    avg_voltage  = df["Voltage"].mean()
    avg_current  = df["Current"].mean()

    total_cost   = df.loc[df["Status"] == "Faulty", "Est_Cost_INR"].sum()

    critical_cnt = (df["Risk_Level"] == "Critical").sum()
    high_cnt     = (df["Risk_Level"] == "High").sum()

    fault_by_area = (
        df[df["Status"] == "Faulty"]
        .groupby("Area")
        .size()
        .sort_values(ascending=False)
    )
    top_area      = fault_by_area.index[0] if len(fault_by_area) else "—"
    top_area_cnt  = int(fault_by_area.iloc[0]) if len(fault_by_area) else 0

    return {
        "total":         int(total),
        "working":       int(working),
        "faulty":        int(faulty),
        "fault_pct":     round(fault_pct, 1),
        "health_score":  round(health_score, 1),
        "avg_voltage":   round(avg_voltage, 1),
        "avg_current":   round(avg_current, 3),
        "total_cost":    int(total_cost),
        "critical_cnt":  int(critical_cnt),
        "high_cnt":      int(high_cnt),
        "top_area":      top_area,
        "top_area_cnt":  top_area_cnt,
        "fault_by_area": fault_by_area,
    }


# ─────────────────────────────────────────────
#  AREA RANKING
# ─────────────────────────────────────────────

def area_ranking(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby("Area").agg(
        Total=("Light_ID",   "count"),
        Working=("Status",   lambda x: (x == "Working").sum()),
        Faulty=("Status",    lambda x: (x == "Faulty").sum()),
        Avg_Voltage=("Voltage", "mean"),
        Avg_Current=("Current", "mean"),
        Avg_Risk=("Risk_Score", "mean"),
    ).reset_index()

    grp["Fault_Rate_%"] = (grp["Faulty"] / grp["Total"] * 100).round(1)
    grp["Health_%"]     = (grp["Working"] / grp["Total"] * 100).round(1)
    grp["Rank"]         = grp["Health_%"].rank(ascending=False).astype(int)
    grp = grp.sort_values("Rank")
    return grp


# ─────────────────────────────────────────────
#  PREDICTIVE HELPERS
# ─────────────────────────────────────────────

def predict_failure_probability(row) -> float:
    """Simple heuristic-based failure probability (0-1)."""
    prob = 0.0
    age  = row.get("Age_Years", 5)
    prob += min(age / 15, 0.35)
    if row["Voltage"] < 200:
        prob += 0.25
    if row["Current"] < 0.2:
        prob += 0.30
    if row["Status"] == "Faulty":
        prob += 0.10
    return min(round(prob, 2), 0.99)
