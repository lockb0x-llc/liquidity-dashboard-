# 🏦 US Liquidity Dashboard

A modular, real-time Python application designed to track and visualize systemic liquidity stress indicators in the U.S. financial system. This dashboard monitors key Federal Reserve facilities and market rates to provide forensic visibility into liquidity conditions.

## 🌟 Overview

The dashboard is built using **Streamlit** and follows a modular architecture where each financial indicator is an independent UI component. It integrates directly with public data sources from the New York Fed and the U.S. Treasury.

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

## 🏗️ Architecture

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
│       └── utils.py       # UI consistency helpers
├── data/                  # Local CSV cache
└── docs/                  # Technical documentation
```

## ☁️ Deployment

### Azure App Service (Recommended)
This application is best hosted as an **Azure App Service (Linux Web App)** with Python 3.11+.

1. **Create Resource**: Create a Web App (Python) in the Azure Portal.
2. **Setup Credentials**: 
   - Generate a Service Principal using Azure CLI:
     `az ad sp create-for-rbac --name "myApp" --role contributor --scopes /subscriptions/<sub-id>/resourceGroups/<rg-name> --sdk-auth`
   - Add the resulting JSON to GitHub Secrets as `AZURE_CREDENTIALS`.
3. **Setup CI/CD**: The workflow in `.github/workflows/azure-app-service-deployment.yml` will now use these credentials.
4. **Startup Command**: In Azure Portal, set the startup command to:
   `streamlit run streamlit_app.py --server.port 8000 --server.address 0.0.0.0`


### Azure Static Web Apps
If you prefer **Azure Static Web Apps**, ensure you are using a static site generator like **Stlite** to bundle the Python environment into WebAssembly.

## ⚙️ Configuration

Alert thresholds and API endpoints can be modified in `src/config.py`:
- `THRESHOLDS`: Configure levels for stress detection.
- `DATA_SOURCES`: API endpoints for the Federal Reserve and Treasury.

## 📚 Data Sources
- [NY Fed Markets Data API](https://markets.newyorkfed.org/api/)
- [U.S. Treasury Fiscal Data](https://api.fiscaldata.treasury.gov/)
- [Federal Reserve H.4.1 Release](https://www.federalreserve.gov/releases/h41/)

---

![Screenshot](docs/Screenshot_2-1-2026_175926_localhost.png)

*Built for macro analysts and financial engineers seeking transparency in systemic liquidity.*
