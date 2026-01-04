# 🧠 Liquidity Stress Dashboard Architecture

This documentation describes the modular architecture of the US Liquidity Dashboard. The system is designed for extensibility, where each financial indicator is encapsulated in its own data fetcher and UI component.

## 📦 Project Structure

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

---

## 🚀 Usage

### 1. Set Up
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Locally
```bash
streamlit run streamlit_app.py
```

## ☁️ Deployment

### Azure App Service (Recommended)
Since Streamlit is a server-side Python application, **Azure App Service** is the preferred hosting platform.

1. **Create Web App**: In the Azure Portal, create a "Web App" with the **Python** runtime.
2. **Configuration**: 
   - Set the startup command to: `streamlit run streamlit_app.py --server.port 8000 --server.address 0.0.0.0`
   - Ensure the port matches the one configured in Azure (usually 8000).
3. **CI/CD**: Use the GitHub Actions provided by Azure to automate deployment on push.

### Azure Static Web Apps
Azure Static Web Apps is primarily for static content and serverless APIs. To run Streamlit here:
- You must use **Stlite** (Streamlit in the browser via WebAssembly).
- Alternatively, host the Streamlit app on App Service and use Static Web Apps only for static documentation or landing pages.

---

## 🛠️ Extending the Dashboard

### Adding a New Indicator
1. **Create a Fetcher**: Add `src/fetch_[name].py`. Inherit from existing patterns to fetch from APIs (NY Fed, FRED, etc.).
2. **Add a Panel**: Add `src/components/[name]_panel.py`. Use `render_metric_card` and `make_chart_container` from `src/components/utils.py` for UI consistency.
3. **Integrate**: Add the new panel to `streamlit_app.py` in the appropriate grid row.

### Configuration
Update `src/config.py` to add new API endpoints or adjust stress thresholds.
