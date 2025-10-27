# 🧠 Liquidity Stress Dashboard

A modular Python application that tracks and visualizes systemic liquidity stress indicators in the U.S. financial system, including ON RRP (Reverse Repo), Repo, bank reserves, SOFR, SRF usage, and Treasury issuance. Designed for forensic analysts, macro strategists, and capital allocators.

## 🚦 Current State & API Endpoints

All data is fetched live from official APIs. No mock or fallback data is used. The dashboard supports:
- **ON RRP & Repo**: https://markets.newyorkfed.org/api/rp/results/search.json?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD&operationTypes=Reverse%20Repo|Repo&method=multiple
- **Bank Reserves**: https://www.federalreserve.gov/releases/h41/current/
- **SOFR**: https://markets.newyorkfed.org/api/rates/secured/sofr/search.json
- **SRF**: https://markets.newyorkfed.org/api/rp/standingrepofacility/search.json
- **Treasury Auctions**: https://api.fiscaldata.treasury.gov/services/api/v1/accounting/od/auctions_query

---

## 📦 Project Structure

```
liquidity-dashboard/
├── data/
│   ├── on_rrp.csv
│   ├── reserves.csv
│   ├── sofr.csv
│   ├── srf.csv
│   └── treasury_auctions.csv
├── src/
│   ├── fetch_on_rrp.py
│   ├── fetch_reserves.py
│   ├── fetch_sofr.py
│   ├── fetch_srf.py
│   ├── fetch_treasury.py
│   ├── plot_dashboard.py
│   └── utils.py
├── dashboard.py
├── requirements.txt
└── README.md
```

---

## 🚀 Features

- 📉 **ON RRP Balance Tracker** — visualizes daily reverse repo usage from NY Fed
- 📉 **Repo Tracker** — visualizes daily repo usage from NY Fed
- 🏦 **Bank Reserve Monitor** — tracks total reserves from Fed H.4.1 release
- 🔁 **SRF Usage** — flags emergency liquidity injections
- 💸 **SOFR Rate Monitor** — detects repo market stress
- 🧾 **Treasury Issuance Calendar** — overlays auction pressure on liquidity
- 📊 **Threshold Alerts** — highlights when reserves approach 2019 crisis levels
- 🧱 **Modular Design** — each data source is independently fetchable and plottable

- 🟦 **Operation Type Selector** — dashboard allows user to select Repo, Reverse Repo, or both for analysis
- 📊 **Multi-indicator Visualization** — interactive charts for accepted amounts, rates, counterparties, and more
- 🧮 **Summary Metrics** — latest operation stats, rolling averages, and stress flags
- 🧰 **Interactive Table** — sortable/filterable operation details
- 📈 **Distribution & Trend Analysis** — histograms, time series, and comparison charts

---

## 🔧 Setup Instructions

1. **Clone the repo**  
   ```bash
   git clone https://github.com/yourusername/liquidity-dashboard.git
   cd liquidity-dashboard
   ```

2. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard**  
   ```bash
   python dashboard.py
   ```

---

## 📥 Data Sources (Free + Public)

| Module         | API Endpoint                                                                |
|----------------|-----------------------------------------------------------------------------|
| ON RRP/Repo    | https://markets.newyorkfed.org/api/rp/results/search.json                   |
| Bank Reserves  | https://www.federalreserve.gov/releases/h41/current/                        |
| SRF Usage      | https://markets.newyorkfed.org/api/rp/standingrepofacility/search.json      |
| SOFR Rate      | https://markets.newyorkfed.org/api/rates/secured/sofr/search.json           |
| Treasury Auctions | https://api.fiscaldata.treasury.gov/services/api/v1/accounting/od/auctions_query |

---

## 🧠 Core Logic (Copilot Guidance)

### `dashboard.py`
- Imports all fetch and plot modules
- Calls each fetcher to update local CSVs
- Loads data and generates a composite dashboard using `matplotlib` or `plotly`

### `streamlit_dashboard.py`
- Interactive dashboard using Streamlit
- Operation type selector for Repo/Reverse Repo
- Fetches live data for selected types and date ranges
- Visualizes accepted amounts, rates, counterparties, and more
- Interactive Altair charts and tables
- Summary metrics and stress flags

### `fetch_on_rrp.py`
- Scrapes or downloads ON RRP data from NY Fed
- Outputs `data/on_rrp.csv` with columns: `Date`, `Balance_Billions`

- Uses NY Fed API for both Reverse Repo and Repo operations
- Supports latest, last N, and date range queries
- No mock data; only real API responses

### `fetch_reserves.py`
- Parses Fed H.4.1 HTML or CSV
- Extracts total reserves (Table 1, line 8)
- Outputs `data/reserves.csv` with `Date`, `Reserves_Trillions`

- Uses official H.4.1 endpoint
- Handles HTML parsing and error cases

### `fetch_sofr.py`
- Pulls SOFR from NY Fed
- Outputs `data/sofr.csv` with `Date`, `SOFR_Rate`

- Uses NY Fed SOFR API
- Handles missing fields and data cleaning

### `fetch_srf.py`
- Scrapes SRF usage from NY Fed repo operations
- Outputs `data/srf.csv` with `Date`, `SRF_Usage_Billions`

- Uses NY Fed SRF API
- Flags emergency usage and stress events

### `fetch_treasury.py`
- Scrapes Treasury auction calendar
- Outputs `data/treasury_auctions.csv` with `Date`, `Instrument`, `Amount_Billions`

- Uses FiscalData Treasury API
- Handles multiple endpoints and data formats

### `plot_dashboard.py`
- Loads all CSVs
- Plots:
  - ON RRP trend
  - Reserves with $2.8T threshold line
  - SOFR rate spikes
  - SRF usage bars
  - Treasury auction overlays
- Saves or displays composite dashboard

### Lessons Learned
- NY Fed API endpoints require precise parameters and operation type
- Date range queries must use `search.json` with `operationTypes` and `method=multiple`
- All mock/fallback logic removed; only real API data is used
- Error handling for empty DataFrames and failed requests is essential
- Field mapping must match API response structure
- Dashboard must allow user selection of operation type and date range
- Visualization should support multi-indicator, interactive analysis

---

## 📈 Example Output

- Line chart: ON RRP balance over time
- Line chart: Bank reserves with crisis threshold
- Bar chart: SRF usage
- Line chart: SOFR rate
- Calendar overlay: Treasury auction sizes

## 📋 Implementation Plan (Next Steps)

1. **Visualization Enhancements**
   - Add time series line charts for accepted amounts, rates, and counterparties
   - Add histograms for accepted amount distribution
   - Add interactive tables with sorting/filtering
   - Add summary metrics and rolling averages
   - Add multi-indicator comparison charts (Repo vs Reverse Repo)
2. **Dashboard Features**
   - Sidebar controls for date range and operation type selection
   - Downloadable CSVs for all data views
   - Stress flags and alert banners for threshold breaches
3. **Documentation & Reference**
   - Keep API references and field mappings up to date
   - Document all dashboard features and user controls
4. **Testing & Validation**
   - Validate all fetchers against live API data
   - Test dashboard with various date ranges and operation types
5. **Lessons Integration**
   - Apply error handling and field mapping lessons to all modules
   - Ensure dashboard is robust to API changes and empty data
6. **Release & Feedback**
   - Finalize dashboard UI and documentation
   - Gather user feedback and iterate on features

---

## 🧪 Future Enhancements

- Add CLI flags for individual modules
- Automate daily fetch via cron or GitHub Actions
- Integrate with FRED API for cleaner reserve data
- Add asset overlays (e.g., SHV, VIXY, UUP) for tactical signals
- Export dashboard as HTML or PDF
