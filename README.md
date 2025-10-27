# 🏦 Fed Liquidity Stress Dashboard

A comprehensive modular Python application that tracks and visualizes systemic liquidity stress indicators in the U.S. financial system, including ON RRP balances, bank reserves, SOFR, SRF usage, and Treasury issuance. Designed for forensic analysts, macro strategists, and capital allocators.

## 🎯 Features

### Core Monitoring Capabilities
- **ON RRP (Overnight Reverse Repo)** - Daily reverse repo usage from NY Fed
- **Bank Reserves** - Total reserves from Fed H.4.1 release  
- **SOFR (Secured Overnight Financing Rate)** - Rate volatility and volume monitoring
- **SRF (Standing Repo Facility)** - Emergency liquidity injection detection
- **Treasury Auctions** - Issuance pressure and yield trend analysis

### Stress Detection & Alerts
- 🚨 **Real-time threshold monitoring** with configurable alert levels
- 📊 **Multi-indicator stress analysis** for comprehensive risk assessment
- ⚠️ **Emergency liquidity usage flagging** (SRF activation detection)
- 📈 **Trend analysis** with moving averages and volatility calculations
- 🎯 **Automated reporting** with stress level summaries

### Visualization & Analysis
- 📈 **Interactive dashboards** with comprehensive plots for each indicator
- 🎨 **System overview dashboard** showing all stress indicators 
- 📊 **Historical trend analysis** with configurable time periods
- 💹 **Volatility monitoring** and anomaly detection
- 📋 **Export functionality** for further analysis

## 📁 Project Structure

```
liquidity-dashboard/
├── dashboard.py           # Main orchestrator application
├── plot_dashboard.py      # Visualization and plotting module
├── test_dashboard.py      # Simplified demo version
├── requirements.txt       # Python dependencies
├── data/                  # CSV data storage
└── src/                   # Core modules
    ├── __init__.py
    ├── config.py          # Configuration and thresholds
    ├── utils.py           # Common utilities
    ├── fetch_onrrp.py     # ON RRP data fetcher
    ├── fetch_reserves.py  # Bank reserves data fetcher
    ├── fetch_sofr.py      # SOFR rate data fetcher
    ├── fetch_srf.py       # SRF usage data fetcher
    └── fetch_treasury.py  # Treasury auction data fetcher
```

## 📊 Data Sources

- **NY Fed Markets**: ON RRP, SOFR, SRF data
- **Federal Reserve H.4.1**: Bank reserves and monetary base
- **Treasury.gov API**: Auction results and issuance data


## 🚀 Running Locally

```bash
git clone <your-repo-url>
cd liquidity-dashboard-
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_dashboard.py
```

## ☁️ Deploying to Azure Web Apps (App Service)

You can deploy this dashboard to Azure Web Apps using VS Code and the Azure Tools extension pack:

1. **Install Azure Tools Extension Pack** in VS Code.
2. **Sign in to Azure** in VS Code.
3. **Open your project folder** in VS Code.
4. Open the Command Palette (`Cmd+Shift+P`), run `Azure: Create Web App`, and follow prompts:
    - Select your subscription
    - Choose a unique app name
    - Select Python 3.x runtime
    - Choose your region
5. When prompted, select your project folder for deployment.
6. In the Azure portal or VS Code, set the startup command:
    ```
    streamlit run streamlit_dashboard.py --server.port 8000 --server.address 0.0.0.0
    ```
    (Set this in the "Startup Command" field under "Configuration" in the Azure portal.)
7. Ensure your `requirements.txt` is present and up to date.
8. Deploy using `Azure: Deploy to Web App` in VS Code.
9. Access your dashboard via the provided Azure URL.

**Troubleshooting:**
- If you see a blank page, check the Azure Web App logs for errors.
- Make sure the port and address are set as above.
- Ensure all dependencies are listed in `requirements.txt`.

---
### Default Stress Thresholds
- **ON RRP Stress Level**: $2,000B (indicates high money market stress)
- **Bank Reserves Low**: $3,000B (indicates potential liquidity constraints) 
- **SOFR Spike**: 0.25% above recent average (repo market stress)
- **SRF Emergency Usage**: $50B (emergency liquidity facility activation)
- **Treasury High Issuance**: $50B/week (debt market pressure)

### Customization
Edit `src/config.py` to modify:
- Data source endpoints
- Alert thresholds  
- File paths
- Plotting configurations

## 🔧 Installation

### Production Version
```bash
# Install dependencies
pip install -r requirements.txt

# Run dashboard
python3 dashboard.py
```

### Demo Version (No Dependencies)
```bash
# Run immediately with built-in Python
python3 test_dashboard.py
```

## 📈 Usage Examples

### Individual Module Analysis
```bash
# Analyze ON RRP stress levels
python3 dashboard.py --module onrrp

# Check for SRF emergency usage
python3 dashboard.py --module srf

# Treasury issuance pressure analysis
python3 dashboard.py --module treasury
```

### Historical Analysis
```bash
# Analyze specific period
python3 dashboard.py --start-date 2023-03-01 --end-date 2023-04-01

# Banking crisis period analysis
python3 dashboard.py --start-date 2023-03-08 --end-date 2023-03-31
```

## 🎯 Key Indicators Explained

### ON RRP (Overnight Reverse Repo)
- **Normal Range**: $1.5-2.5 trillion
- **Stress Indicator**: >$2.0 trillion suggests money market stress
- **Significance**: High usage indicates banks/MMFs parking excess cash at Fed

### Bank Reserves  
- **Normal Range**: $3.0-4.0 trillion
- **Stress Indicator**: <$3.0 trillion suggests potential liquidity constraints
- **Significance**: Declining reserves can indicate banking system stress

### SOFR (Secured Overnight Financing Rate)
- **Normal Behavior**: Stable around Fed Funds rate
- **Stress Indicator**: Spikes >25bp above trend indicate repo market stress
- **Significance**: Primary reference rate for $200+ trillion in financial products

### SRF (Standing Repo Facility)
- **Normal Usage**: $0 (emergency facility)
- **Stress Indicator**: ANY usage indicates emergency liquidity needs
- **Significance**: Fed's backstop for repo market disruptions

### Treasury Issuance
- **Normal Range**: $30-60B per week
- **Stress Indicator**: >$50B/week sustained issuance
- **Significance**: High issuance can indicate fiscal stress or market capacity constraints

## 🚨 Alert System

The dashboard provides automated monitoring with three alert levels:

- 🟢 **NORMAL**: All indicators within expected ranges
- ⚠️ **STRESS**: One or more indicators exceed thresholds  
- 🚨 **EMERGENCY**: SRF usage detected (critical liquidity event)

## 📊 Sample Output

```
🏦 FEDERAL LIQUIDITY STRESS DASHBOARD REPORT
===============================================
⚠️  LIQUIDITY STRESS DETECTED (2 indicators)

   • ON RRP: $2,350.0B (above $2,000B threshold)
   • Treasury Issuance: $113.0B/week (above $50B threshold)

📈 LATEST READINGS
ON RRP: $2,350.0B (90 participants) 🔴 STRESS
Bank Reserves: $3,700.0B 🟢 NORMAL  
SOFR Rate: 5.380% (Volume: $2,100.0B) 🟢 NORMAL
SRF Usage: $0.0B 🟢 NORMAL
Treasury Issuance: $113.0B/week 🔴 HIGH
```

## 🤝 Contributing

This project is designed for financial market monitoring and analysis. Each module fetches and plots independently, with `dashboard.py` running the full integrated analysis.

## 📚 Background

The Federal Reserve's liquidity facilities and overnight funding markets are critical components of financial system stability. This dashboard provides real-time monitoring of key stress indicators that have historically preceded or coincided with financial market disruptions.

Built for forensic analysts, macro strategists, and capital allocators who need comprehensive visibility into Fed liquidity conditions and systemic stress indicators.
