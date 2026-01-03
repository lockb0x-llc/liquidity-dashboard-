import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from src.fetch_srf import SRFFetcher
from src.components.utils import make_panel_header, render_metric_card, make_chart_container

def render_srf_panel():
    """
    Renders the Standing Repo Facility (SRF) component.
    """
    make_panel_header("Standing Repo Facility")

    # Fetch data
    try:
        fetcher = SRFFetcher()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        df = fetcher.fetch_data(start_date=start_date, end_date=end_date)
    except Exception as e:
        st.error(f"Failed to fetch SRF data: {e}")
        return

    if df is None or df.empty:
        st.info("No recent SRF activity detected (Normal).")
        return

    # Standarized columns from SRFFetcher: date, usage_billions, participants, rate
    if 'date' not in df.columns or 'usage_billions' not in df.columns:
        st.warning("SRF Data format error.")
        return
        
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    latest = df.iloc[-1]
    
    # Metrics
    render_metric_card(
        "Latest Usage", 
        f"${latest['usage_billions']:.2f}B",
        help_text="Total amount accepted in latest operation"
    )

    # Chart
    if len(df) > 1:
        fig = px.bar(
            df, 
            x="date", 
            y="usage_billions", 
            title="SRF Usage History",
            labels={"usage_billions": "Volume ($B)"}
        )
        make_chart_container(fig)
