# 🏦 US Liquidity Dashboard

A modular, real-time Python application designed to track and visualize systemic liquidity stress indicators in the U.S. financial system. This dashboard monitors key Federal Reserve facilities and market rates to provide forensic visibility into liquidity conditions.

## 🌟 Overview

The dashboard is built using **Streamlit** and follow a modular architecture where each financial indicator is a independent UI component. It integrates directly with public data sources from the New York Fed and the U.S. Treasury.

### Featured Indicators:
- **ON RRP (Overnight Reverse Repo)**: Daily usage of the Fed's cash-drain facility.
- **Bank Reserves**: Total reserve balances from the Fed H.4.1 release.
- **SOFR (Secured Overnight Financing Rate)**: Reference rate volatility and volume.
- **SRF (Standing Repo Facility)**: Detection of emergency liquidity backstop usage.
- **Treasury Issuance**: Weekly auction volumes and yield trends.

## 🚀 Quick Start

### 1. Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd liquidity-dashboard-

# Set up virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch Dashboard
```bash
streamlit run streamlit_app.py
```

## �️ Architecture

The project is organized for modularity and maintainability:

```
liquidity-dashboard/
├── streamlit_app.py       # Main dashboard entry point
├── requirements.txt       # Project dependencies
├── src/
│   ├── fetch_*.py         # Robust data fetchers for each indicator
│   ├── config.py          # Centralized API endpoints and thresholds
│   ├── utils.py           # Shared data processing utilities
│   └── components/        # Modular UI panels
│       ├── onrrp_panel.py
│       ├── treasury_panel.py
│       ├── sofr_panel.py
│       ├── srf_panel.py
│       ├── reserves_panel.py
│       └── utils.py       # UI consistency helpers (Glassmorphism, Metrics)
├── data/                  # Local CSV cache for historical analysis
└── docs/                  # Technical documentation
```

## 📈 Key Functionality

- **Modular Panels**: Each indicator has its own self-contained logic for fetching data and rendering charts.
- **Stress Alerts**: Visual indicators for when metrics exceed historical stress thresholds (e.g., ON RRP > $2T, Low Reserves).
- **Interactive Charts**: Responsive Plotly visualizations for trend analysis.
- **Live Data**: Fetches the latest available results from the NY Fed Markets API and Treasury Fiscal Data service.

## ⚙️ Configuration

Alert thresholds and API endpoints can be modified in `src/config.py`:
- `THRESHOLDS`: Configure levels for stress detection.
- `DATA_SOURCES`: API endpoints for the Federal Reserve and Treasury.

## � Data Sources
- [NY Fed Markets Data API](https://markets.newyorkfed.org/api/)
- [U.S. Treasury Fiscal Data](https://api.fiscaldata.treasury.gov/)
- [Federal Reserve H.4.1 Release](https://www.federalreserve.gov/releases/h41/)

---
*Built for macro analysts and financial engineers seeking transparency in systemic liquidity.*
