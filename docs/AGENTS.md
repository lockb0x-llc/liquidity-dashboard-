# 🧠 Liquidity Stress Dashboard (Applet Monorepo)

This documentation describes the monorepo architecture for modular liquidity applets. Each applet is a self-contained Python module for a specific data source or visualization. The current implementation focuses on the ON RRP applet.

## 📦 Monorepo Structure

```
liquidity-dashboard-
├── applets/
│   └── onrrp/
│       ├── __init__.py
│       └── fetch_onrrp.py   # ON RRP applet code
├── src/
│   └── common/
│       ├── config.py        # Shared configuration
│       └── utils.py         # Shared utilities
├── dashboard.py             # Main ON RRP dashboard (CLI)
├── streamlit_dashboard.py   # ON RRP Streamlit dashboard
├── requirements.txt         # Python dependencies
├── data/                    # CSV data storage
└── docs/
    └── AGENTS.md            # Architecture and usage notes
```

## 🚀 Usage

### 1. Clone and Set Up

```bash
git clone <your-repo-url>
cd liquidity-dashboard-
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Prepare Data

Place your ON RRP data CSV in the `data/` directory as `on_rrp.csv` (if not using live API).

### 3. Run the CLI Dashboard

```bash
python dashboard.py
```
Displays the latest ON RRP data and a stress analysis summary in the terminal.

### 4. Run the Streamlit Dashboard

```bash
streamlit run streamlit_dashboard.py
```
Launches an interactive web dashboard focused on ON RRP data and stress detection.

### 5. Add More Applets

To add new applets (e.g., for Reserves, SOFR, SRF, Treasury):
- Create a new folder in `applets/` (e.g., `applets/reserves/`)
- Implement fetch and analysis logic in that folder
- Update the main dashboard to import and use the new applet

## 🛠️ Extending the Dashboard
- Follow the applet pattern for new indicators.
- Use `src/common/` for shared logic.
- Document new applets in this file and the README.
