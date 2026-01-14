import streamlit as st
import plotly.express as px
from src.api_client import LiquidityAPIClient
from src.components.utils import make_panel_header, render_metric_card, make_chart_container

def render_reserves_panel():
    """
    Renders the Federal Reserve Total Reserves component.
    """
    make_panel_header("Fed Total Reserves")

    # Fetch data
    try:
        client = LiquidityAPIClient()
        # Fetch 90 days of data
        df = client.get_reserves(days=90)
    except Exception as e:
        st.error(f"Failed to fetch Reserves data: {e}")
        return

    if df is None or df.empty:
        st.warning("No Reserves data available.")
        return

    # Standardized columns from ReservesFetcher: date, reserves_billions
    if 'date' not in df.columns or 'reserves_billions' not in df.columns:
        st.warning("Reserves data format error.")
        return

    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    latest = df.iloc[-1]
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_metric_card(
            "Total Reserves", 
            f"${latest['reserves_billions']:,.0f}B",
            help_text="Total Reserve Balances maintained"
        )
    
    # Change from previous period
    if len(df) > 1:
        prev = df.iloc[-2]
        change = latest['reserves_billions'] - prev['reserves_billions']
        with col2:
             render_metric_card(
                "Recent Change", 
                f"{change:+.1f}B",
                delta=f"{change:+.1f}B",
                help_text="Change in reserves since last release"
            )

    # Chart
    fig = px.line(
        df, 
        x="date", 
        y="reserves_billions", 
        title="Total Reserves Trend",
        labels={"reserves_billions": "Reserves ($B)", "date": "Date"}
    )
    make_chart_container(fig)
