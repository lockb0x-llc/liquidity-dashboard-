import streamlit as st
import plotly.express as px
from src.api_client import LiquidityAPIClient
from src.components.utils import make_panel_header, render_metric_card, make_chart_container

def render_treasury_panel():
    """
    Renders the Treasury Issuance component.
    """
    make_panel_header("Treasury Issuance")

    # Fetch data
    try:
        client = LiquidityAPIClient()
        df = client.get_treasury(days=90)
    except Exception as e:
        st.error(f"Failed to fetch Treasury data: {e}")
        return

    if df is None or df.empty:
        st.warning("No Treasury data available.")
        return

    # Calculate weekly issuance
    df['Week'] = df['date'].dt.to_period('W').apply(lambda r: r.start_time)
    weekly = df.groupby('Week')['amount_billions'].sum().reset_index()
    
    if weekly.empty:
        st.warning("Insufficient data for weekly analysis.")
        return

    latest_week = weekly.iloc[-1]
    prev_week = weekly.iloc[-2] if len(weekly) > 1 else None
    
    delta = None
    if prev_week is not None:
        delta = f"{latest_week['amount_billions'] - prev_week['amount_billions']:.1f}B"

    col1, col2 = st.columns(2)
    
    with col1:
        render_metric_card(
            "Weekly Issuance", 
            f"${latest_week['amount_billions']:.1f}B",
            delta=delta,
            help_text="Total issuance for the current week"
        )
    
    # Latest Yield (using the most recent auction record)
    latest_auction = df.iloc[-1]
    with col2:
        render_metric_card(
            "Latest Yield",
            f"{latest_auction['yield_rate']:.2f}%" if 'yield_rate' in df.columns else "N/A",
            help_text=f"Yield for {latest_auction.get('security_type', 'latest auction')}"
        )

    # Chart
    fig = px.bar(
        weekly, 
        x="Week", 
        y="amount_billions", 
        title="Weekly Issuance Trend (90 Days)",
        labels={"amount_billions": "Issuance ($B)"}
    )
    make_chart_container(fig)
