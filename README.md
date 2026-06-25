# 🏙️ SmartCity OS — Street Light Analytics Platform

> **Production-grade Smart City Dashboard** built with Streamlit, Plotly, and Folium.
> Designed for Final Year Projects, Placement Portfolios, Hackathons, and Smart City Demonstrations.

---

## 🚀 Quick Start

```bash
# 1. Clone / extract the project
cd smart_city_platform

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the platform
streamlit run Dashboard.py
```

---

## 📂 Project Architecture

```
smart_city_platform/
│
├── Dashboard.py                 # 🏠 Executive Command Center (main entry)
│
├── pages/
│   ├── 1_Analytics.py           # 📊 Advanced Analytics — Plotly interactive charts
│   ├── 2_Risk_Analysis.py       # 🚨 Risk Intelligence — Scoring, alerts, predictions
│   ├── 3_Maintenance.py         # 🛠️ Maintenance Intelligence — Priority engine, cost
│   ├── 4_Map.py                 # 📍 Smart GIS Map — Folium with rich popups
│   ├── 5_Reports.py             # 📄 Reports & Export — CSV, Excel, PDF-ready
│   └── 6_Predictive_AI.py       # 🤖 Predictive AI — Forecasting, decision support
│
├── utils/
│   ├── __init__.py
│   ├── data_utils.py            # Data loading, KPI computation, risk scoring
│   └── styles.py                # Centralised CSS, components, Plotly theme
│
├── data/
│   └── street_lights.csv        # Primary dataset (20 lights across 5 zones)
│
├── .streamlit/
│   └── config.toml              # Dark theme + server configuration
│
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## 🧠 Feature Overview

### 🏠 Executive Dashboard
- Real-time KPI cards (gradient, glassmorphism design)
- Network health gauge
- Area performance ranking with health % progress bars
- Smart alert system (Critical / Warning / OK banners)
- AI recommendations panel
- Top fault alerts with risk badges

### 📊 Analytics
- Interactive Plotly pie, bar, violin, scatter, histogram charts
- Working vs Faulty grouped bar by area
- Voltage / Current profiling with thresholds
- Risk score heatmap
- Area deep-dive drill-down section
- Analytical insights summary

### 🚨 Risk Analysis
- 0–100 composite risk scoring model
- Critical / High / Medium / Low risk classification
- Predictive failure probability (AI model)
- Risk bubble scatter (Voltage × Current × Failure Prob)
- Area-wise stacked risk chart
- Risk register table with progress columns

### 🛠️ Maintenance Intelligence
- Priority engine (Critical → High → Medium → Low)
- Dynamic cost estimation with configurable pricing
- Technician workload planner (configurable team size)
- SLA-driven maintenance schedule table
- Cost treemap by Area → Priority → Light
- Resource planning summary
- Export maintenance schedule as CSV

### 📍 Smart GIS Map
- CartoDB dark_matter / positron / OpenStreetMap tiles
- Color-coded markers (green = working, red = faulty)
- Risk-coloured fault circles overlay
- Rich HTML popups with full light details
- MarkerCluster option
- MiniMap overlay
- Legend panel
- Area filter, status filter, risk level filter

### 📄 Reports & Export
- Executive Summary with KPI cards + charts
- Fault Report with chart + CSV download
- Maintenance Schedule report + CSV download
- Full dataset export: CSV + Excel (multi-sheet workbook)
- Column selector for custom exports

### 🤖 Predictive AI
- Heuristic failure probability model (voltage + current + age)
- 30/60/90-day fault forecast with confidence band
- Age vs Failure Probability scatter with trendline
- Priority watch list
- Smart City KPI Scorecard
- Decision support engine
- AI-generated action recommendations

---

## 📊 Dataset Schema

| Column            | Type    | Description                     |
|-------------------|---------|---------------------------------|
| Light_ID          | string  | Unique identifier (SL001–SL020) |
| Area              | string  | Zone: North/South/East/West/Central |
| Voltage           | float   | Supply voltage (V)              |
| Current           | float   | Operating current (A)           |
| Status            | string  | Working / Faulty                |
| Latitude          | float   | GPS latitude                    |
| Longitude         | float   | GPS longitude                   |
| Install_Year      | int     | Year of installation            |
| Last_Maintenance  | date    | Date of last maintenance visit  |

**Computed columns** (auto-generated at runtime):
`Risk_Score`, `Risk_Level`, `Priority`, `Action`, `Est_Cost_INR`,
`Health_Score`, `Age_Years`, `Failure_Prob`

---

## 🎨 Design System

| Element           | Specification                                  |
|-------------------|------------------------------------------------|
| Font              | Inter (Google Fonts)                           |
| Background        | `linear-gradient(135deg, #0f0c29, #24243e)`    |
| Primary Accent    | Indigo `#6366f1` / Purple `#8b5cf6`           |
| KPI Cards         | Gradient + glassmorphism + hover lift          |
| Charts            | Plotly dark theme, transparent background      |
| Map Tiles         | CartoDB dark_matter (default)                  |
| Status Colors     | Green `#10b981` / Red `#ef4444`               |
| Risk Colors       | Red / Orange / Yellow / Green                  |

---

## 🏆 Why This Is Placement-Ready

1. **Modular architecture** — `utils/` separates data, styling, and logic
2. **Plotly charts** — interactive, professional, industry-standard
3. **Risk scoring model** — demonstrates analytical thinking
4. **Predictive AI layer** — shows ML awareness even with heuristics
5. **Folium GIS map** — real-world GIS tooling
6. **Multi-format export** — CSV + Excel (openpyxl multi-sheet)
7. **Configurable parameters** — cost inputs, workforce sliders
8. **Dark enterprise UI** — resembles commercial analytics products
9. **Smart City narrative** — framed for municipal/government clients
10. **Decision support** — outputs actionable business intelligence

---

## 📦 Dependencies

```
streamlit>=1.32.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
folium>=0.15.0
streamlit-folium>=0.18.0
openpyxl>=3.1.0
```

---

## 👤 Author

**SmartCity OS v3.0** — Built for Final Year Engineering Projects & Smart City Demonstrations  
Stack: `Python · Streamlit · Plotly · Folium · Pandas · NumPy`

---

*This platform simulates a production-grade municipal analytics dashboard.
For real deployments, replace the CSV data source with a live PostgreSQL / InfluxDB feed
and the heuristic AI model with a trained LSTM or Prophet time-series model.*
Updated deployment