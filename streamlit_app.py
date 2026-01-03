
import streamlit as st
from src.components.utils import load_css
from src.components.onrrp_panel import render_onrrp_panel
from src.components.treasury_panel import render_treasury_panel
from src.components.sofr_panel import render_sofr_panel
from src.components.srf_panel import render_srf_panel
from src.components.reserves_panel import render_reserves_panel

# Page Config
st.set_page_config(
    page_title="Liquidity Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Custom CSS
load_css()

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🏦 US Liquidity Dashboard")
    st.markdown("Real-time monitoring of key financial liquidity indicators.")
with col2:
    if st.button("🔄 Refresh Data", type="primary"):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# Main Grid Layout
# Row 1: ON RRP and Treasury (Key Indicators)
row1_1, row1_2 = st.columns(2)

with row1_1:
    with st.container():
        render_onrrp_panel()

with row1_2:
    with st.container():
        render_treasury_panel()

st.markdown("---")

# Row 2: SOFR and Reserves (Market Rates & System Liquidity)
row2_1, row2_2 = st.columns(2)

with row2_1:
    with st.container():
        render_sofr_panel()

with row2_2:
    with st.container():
        render_reserves_panel()

st.markdown("---")

# Row 3: SRF (Stress Indicator)
row3_1, row3_2 = st.columns([1, 1])

with row3_1:
    with st.container():
        render_srf_panel()

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    Data Sources: NY Fed, US Treasury. | Created with Streamlit.
</div>
""", unsafe_allow_html=True)
