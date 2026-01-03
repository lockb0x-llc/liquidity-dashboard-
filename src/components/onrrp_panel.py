
import streamlit as st
import plotly.express as px
from src.fetch_onrrp import ONRRPFetcher
from src.components.utils import make_panel_header, render_metric_card, make_chart_container

def render_onrrp_panel():
    """
    Renders the ON RRP (Overnight Reverse Repo) component.
    """
    make_panel_header("ON RRP Operations")

    # Fetch data
    try:
        fetcher = ONRRPFetcher()
        # Fetching last 30 days for chart context
        df = fetcher.fetch_data(mode="last_n", last_n=30) 
    except Exception as e:
        st.error(f"Failed to fetch ON RRP data: {e}")
        return

    if df is None or df.empty:
        st.warning("No ON RRP data available.")
        return

    # Latest metrics
    latest = df.iloc[0] # API returns sorted by date desc generally, but let's verify sorting
    
    # Ensure sorted by date ascending for charts
    df_chart = df.sort_values(by="Date", ascending=True)
    latest = df_chart.iloc[-1]

    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_metric_card(
            "Accepted Volume", 
            f"${latest['Accepted_Billions']:.2f}B",
            help_text="Total amount accepted by the Fed"
        )
    
    with col2:
        render_metric_card(
            "Counterparties",
            f"{int(latest['Counterparties'])}",
            help_text="Number of participating counterparties"
        )

    with col3:
        render_metric_card(
            "Award Rate",
            f"{latest['Rate']:.2f}%",
            help_text="Interest rate on ON RRP"
        )
            
    # Chart
    fig = px.area(
        df_chart, 
        x="Date", 
        y="Accepted_Billions", 
        title="ON RRP Volume (30 Days)",
        labels={"Accepted_Billions": "Volume ($B)"}
    )
    make_chart_container(fig)
