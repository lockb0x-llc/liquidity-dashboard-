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

### Azure Static Web Apps
This application is hosted on **Azure Static Web Apps**.

1. **Setup Credentials**: 
   - Ensure the `AZURE_STATIC_WEB_APPS_API_TOKEN_YELLOW_DESERT_0C64A9D1E` secret is configured in your GitHub repository.
2. **CI/CD**: The workflow in `.github/workflows/azure-static-web-apps-yellow-desert-0c64a9d1e.yml` handles the build and deployment on merged Pull Requests to `main`.
3. **Important Configuration**:
   - `app_location`: Set to `/` in the workflow file.
   - `output_location`: If using a static build (Stlite), specify the output directory.


---


## 🛠️ Extending the Dashboard

### Adding a New Indicator
1. **Create a Fetcher**: Add `src/fetch_[name].py`. Inherit from existing patterns to fetch from APIs (NY Fed, FRED, etc.).
2. **Add a Panel**: Add `src/components/[name]_panel.py`. Use `render_metric_card` and `make_chart_container` from `src/components/utils.py` for UI consistency.
3. **Integrate**: Add the new panel to `streamlit_app.py` in the appropriate grid row.

### Configuration
Update `src/config.py` to add new API endpoints or adjust stress thresholds.
