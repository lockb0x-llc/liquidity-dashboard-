# 🧠 Liquidity Stress Dashboard

A modular Python application that tracks and visualizes systemic liquidity stress indicators in the U.S. financial system, including ON RRP balances, bank reserves, SOFR, SRF usage, and Treasury issuance. Designed for forensic analysts, macro strategists, and capital allocators.

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
- 🏦 **Bank Reserve Monitor** — tracks total reserves from Fed H.4.1 release
- 🔁 **SRF Usage** — flags emergency liquidity injections
- 💸 **SOFR Rate Monitor** — detects repo market stress
- 🧾 **Treasury Issuance Calendar** — overlays auction pressure on liquidity
- 📊 **Threshold Alerts** — highlights when reserves approach 2019 crisis levels
- 🧱 **Modular Design** — each data source is independently fetchable and plottable

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

| Module         | Source URL                                                                 |
|----------------|-----------------------------------------------------------------------------|
| ON RRP         | https://www.newyorkfed.org/markets/omo-dmm                                  |
| Bank Reserves  | https://www.federalreserve.gov/releases/h41/                               |
| SRF Usage      | https://www.newyorkfed.org/markets/desk-operations/repo                     |
| SOFR Rate      | https://www.newyorkfed.org/markets/reference-rates/sofr                     |
| Treasury Auctions | https://www.treasurydirect.gov/instit/annceresult/press/               |

---

## 🧠 Core Logic (Copilot Guidance)

### `dashboard.py`
- Imports all fetch and plot modules
- Calls each fetcher to update local CSVs
- Loads data and generates a composite dashboard using `matplotlib` or `plotly`

### `fetch_on_rrp.py`
- Scrapes or downloads ON RRP data from NY Fed
- Outputs `data/on_rrp.csv` with columns: `Date`, `Balance_Billions`

### `fetch_reserves.py`
- Parses Fed H.4.1 HTML or CSV
- Extracts total reserves (Table 1, line 8)
- Outputs `data/reserves.csv` with `Date`, `Reserves_Trillions`

### `fetch_sofr.py`
- Pulls SOFR from NY Fed
- Outputs `data/sofr.csv` with `Date`, `SOFR_Rate`

### `fetch_srf.py`
- Scrapes SRF usage from NY Fed repo operations
- Outputs `data/srf.csv` with `Date`, `SRF_Usage_Billions`

### `fetch_treasury.py`
- Scrapes Treasury auction calendar
- Outputs `data/treasury_auctions.csv` with `Date`, `Instrument`, `Amount_Billions`

### `plot_dashboard.py`
- Loads all CSVs
- Plots:
  - ON RRP trend
  - Reserves with $2.8T threshold line
  - SOFR rate spikes
  - SRF usage bars
  - Treasury auction overlays
- Saves or displays composite dashboard

---

## 📈 Example Output

- Line chart: ON RRP balance over time
- Line chart: Bank reserves with crisis threshold
- Bar chart: SRF usage
- Line chart: SOFR rate
- Calendar overlay: Treasury auction sizes

---

## 🧪 Future Enhancements

- Add CLI flags for individual modules
- Automate daily fetch via cron or GitHub Actions
- Integrate with FRED API for cleaner reserve data
- Add asset overlays (e.g., SHV, VIXY, UUP) for tactical signals
- Export dashboard as HTML or PDF
