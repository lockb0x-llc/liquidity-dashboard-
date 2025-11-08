import streamlit as st
import pandas as pd
from applets.onrrp.fetch_onrrp import fetch_onrrp_api, load_onrrp_data

st.set_page_config(page_title="ON RRP Dashboard", layout="wide")
st.title("ON RRP (Overnight Reverse Repo) Dashboard")
st.markdown("""
**ON RRP** (Overnight Reverse Repo) operations are conducted by the NY Fed to manage short-term liquidity. This dashboard displays the latest ON RRP data fetched live from the NY Fed API.
""")

# User controls
onrrp_mode = st.radio("Select data mode:", ["Latest", "From CSV"], horizontal=True)

if onrrp_mode == "Latest":
    onrrp_df = fetch_onrrp_api()
else:
    onrrp_df = load_onrrp_data()

# Data source indicator
if onrrp_df is not None and not onrrp_df.empty:
    st.success("ON/RRP data loaded.")
else:
    st.warning("ON/RRP data is empty or could not be loaded.")

# Display ON/RRP data
if onrrp_df is not None and not onrrp_df.empty:
    rename_map = {
        "operation_date": "Date",
        "accepted_amount": "Accepted_Billions",
        "counterparties": "Counterparties",
        "rate": "Rate",
        "operation_type": "Operation_Type"
    }
    onrrp_df = onrrp_df.rename(columns={k: v for k, v in rename_map.items() if k in onrrp_df.columns})
    st.dataframe(onrrp_df)

    # Plot Accepted_Billions by Date
    if "Date" in onrrp_df.columns and "Accepted_Billions" in onrrp_df.columns:
        import altair as alt
        chart_df = onrrp_df.copy()
        chart_df["Accepted_Billions"] = pd.to_numeric(chart_df["Accepted_Billions"], errors="coerce")
        chart_df["Date"] = pd.to_datetime(chart_df["Date"])
        chart = alt.Chart(chart_df).mark_line(point=True).encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Accepted_Billions:Q", title="Accepted Billions (USD Bn)"),
            tooltip=[
                alt.Tooltip("Date:T", title="Date"),
                alt.Tooltip("Accepted_Billions:Q", title="Accepted Billions", format=".2f"),
                alt.Tooltip("Counterparties:N", title="Counterparties"),
                alt.Tooltip("Rate:Q", title="Rate", format=".2f")
            ]
        ).properties(title="ON/RRP Accepted Amounts")
        st.altair_chart(chart, use_container_width=True)

    # Plot Rate if present
    if "Date" in onrrp_df.columns and "Rate" in onrrp_df.columns:
        st.line_chart(onrrp_df.set_index("Date")["Rate"])

    # Latest operation summary
    required_cols = ["Date", "Accepted_Billions", "Counterparties", "Rate", "Operation_Type"]
    missing_cols = [col for col in required_cols if col not in onrrp_df.columns]
    if not missing_cols:
        latest_row = onrrp_df.iloc[-1]
        date_str = latest_row["Date"].date() if pd.notna(latest_row["Date"]) else "N/A"
        accepted = latest_row["Accepted_Billions"]
        counterparties = latest_row["Counterparties"]
        rate = latest_row["Rate"]
        op_type = latest_row["Operation_Type"]
        accepted_str = f"${accepted:.2f}B" if not pd.isna(accepted) else "N/A"
        counterparties_str = str(counterparties) if not pd.isna(counterparties) else "N/A"
        rate_str = f"{rate:.2f}" if rate is not None else "N/A"
        st.markdown(f"**Latest ON/RRP Operation:**  ")
        st.markdown(f"Date: {date_str}  ")
        st.markdown(f"Accepted Amount: {accepted_str}  ")
        st.markdown(f"Counterparties: {counterparties_str}  ")
        st.markdown(f"Rate: {rate_str}  ")
        st.markdown(f"Operation Type: {op_type}")
    else:
        st.warning(f"Latest ON/RRP Operation: Data missing columns: {', '.join(missing_cols)}. Check API response and field mapping.")

    csv = onrrp_df.to_csv(index=False).encode()
    st.download_button("Download CSV", csv, "on_rrp.csv", "text/csv")
else:
    st.warning("ON/RRP data not available or no results for selected parameters. Raw DataFrame:")
    st.write(onrrp_df)
