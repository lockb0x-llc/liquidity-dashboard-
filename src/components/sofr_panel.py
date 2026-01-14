import streamlit as st
import pandas as pd
import plotly.express as px
from src.api_client import LiquidityAPIClient
from src.components.utils import make_panel_header, render_metric_card, make_chart_container

def render_sofr_panel():
    """
    Renders the SOFR (Secured Overnight Financing Rate) component.
    """
    make_panel_header("SOFR Rates")

    # Fetch data
    try:
        client = LiquidityAPIClient()
        df = client.get_sofr(days=30)
    except Exception as e:
        st.error(f"Failed to fetch SOFR data: {e}")
        return


    if df is None or df.empty:
        st.warning("No SOFR data available.")
        return

    # Ensure date sorting
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by="date")
    
    latest = df.iloc[-1]
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_metric_card(
            "SOFR Rate", 
            f"{latest['sofr_rate']:.2f}%",
            help_text="Secured Overnight Financing Rate"
        )
    
    with col2:
        render_metric_card(
            "Volume",
            f"${latest['volume_billions']:.0f}B",
            help_text="Total transaction volume"
        )

    # Chart
    fig = px.line(
        df, 
        x="date", 
        y="sofr_rate", 
        title="SOFR Rate Trend (30 Days)",
        labels={"sofr_rate": "Rate (%)", "date": "Date"}
    )
    make_chart_container(fig)
