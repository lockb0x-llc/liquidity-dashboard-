
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def make_panel_header(title, updated_at=None):
    """
    Renders a standardized header for metrics panels.
    """
    st.markdown(f"### {title}")
    if updated_at:
        st.caption(f"Last updated: {updated_at}")
    st.markdown("---")

def render_metric_card(label, value, delta=None, help_text=None):
    """
    Renders a metric card.
    """
    st.metric(label=label, value=value, delta=delta, help=help_text)

def make_chart_container(fig, title=None):
    """
    Standardizes chart rendering.
    """
    if title:
        fig.update_layout(title=title)
    st.plotly_chart(fig, use_container_width=True)

def load_css():
    """
    Injects custom CSS for better aesthetics.
    """
    st.markdown("""
        <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 3rem;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
        }
        </style>
    """, unsafe_allow_html=True)
