
import streamlit as st
import pandas as pd

@st.cache_data
def load_transport_data() -> pd.DataFrame:
    """Load and cache transport data from CSV"""
    try:
        df = pd.read_csv("data_transport.csv")

        # Clean price column (spaces + commas)
        if 'price per person ( EUR )' in df.columns:
            df['price per person ( EUR )'] = (
                df['price per person ( EUR )']
                .astype(str)
                .str.replace(" ", "")
                .str.replace(",", ".")
                .astype(float)
            )

        # Convert date
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Error loading transport data: {str(e)}")
        return pd.DataFrame()

def create_flight_metrics(df: pd.DataFrame) -> None:
    """Show flight-related metrics"""
    if df.empty:
        st.warning("No transport data available.")
        return

    # Filter flightss
    flight_df = df[df['type of transport'].str.lower() == "flight"]

    if flight_df.empty:
        st.info("No flight records found in transport data.")
        return

    # --- Metric: total flights
    st.metric("✈️ Flight Tickets", len(flight_df))

    # --- Table: flights from-to-price
    st.write("### ✈️ Flight Details")
    #st.dataframe(flight_df[['from', 'to', 'price per person ( EUR )']], use_container_width=True)
    st.dataframe(
        flight_df[['from', 'to', 'price per person ( EUR )']].copy().reset_index(drop=True),
        use_container_width=True
    )



    # --- Total price
    total_price = flight_df['price per person ( EUR )'].sum()
    st.subheader(f"💶 Total Flight Cost: € {total_price:,.2f}")
