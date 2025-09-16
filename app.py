import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from typing import Dict, Any

# Page configuration
st.set_page_config(
    page_title="Tam Vonku Dashboard",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and cache the accommodation data"""
    try:
        if os.path.exists("travel_data.csv"):
            df = pd.read_csv("travel_data.csv")
            # Handle European number format in cost column
            if 'total price of stay' in df.columns:
                df['total price of stay'] = (
                    df['total price of stay'].astype(str)
                    .str.replace(' ', '')
                    .str.replace(',', '.')
                    .astype(float)
                )
            # Convert date columns to datetime
            date_columns = ['check in', 'check out']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], format='%d.%m.%Y', errors='coerce')
            # Create combined destination column
            if 'country' in df.columns and 'location' in df.columns:
                df['destination'] = df['location'].astype(str) + ', ' + df['country'].astype(str)
            return df
        else:
            st.error("travel_data.csv file not found in the project directory.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

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

def create_summary_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Create summary statistics for the dashboard"""
    if df.empty:
        return {}
    metrics = {}
    # Days on the Road
    if 'check in' in df.columns and 'check out' in df.columns:
        df_dates = df.dropna(subset=['check in', 'check out'])
        if not df_dates.empty:
            first_day = df_dates['check in'].min()
            last_day = df_dates['check out'].max()
            if pd.notna(first_day) and pd.notna(last_day):
                metrics['days_on_road'] = (last_day - first_day).days + 1
    # Basic metrics
    metrics['unique_places_stayed'] = df['accommodation'].nunique()
    if 'country' in df.columns:
        metrics['visited_countries'] = df['country'].nunique()
    # Cost metrics
    cost_columns = ['total price of stay', 'cost', 'price', 'amount', 'total_cost', 'expense']
    cost_col = next((col for col in cost_columns if col in df.columns), None)
    if cost_col:
        metrics['total_cost of accommodation'] = df[cost_col].sum()
        avg_cost = round(df[cost_col].sum() / 2 / metrics.get('days_on_road', 1), 2)
        metrics['average per person per night'] = f'€ {avg_cost}'
    # Destination metrics
    destination_columns = ['destination', 'city', 'country', 'location']
    dest_col = next((col for col in destination_columns if col in df.columns), None)
    if dest_col:
        metrics['unique_destinations'] = df[dest_col].nunique()
        metrics['top_destination'] = df[dest_col].value_counts().index[0] if not df[dest_col].value_counts().empty else "N/A"
    # Platform metrics
    type_columns = ['platform', 'travel_type', 'type', 'category', 'mode']
    type_col = next((col for col in type_columns if col in df.columns), None)
    if type_col and 'accommodation' in df.columns:
        metrics['workaway_projects'] = df[df[type_col].str.lower() == 'workaway']['accommodation'].nunique()
    return metrics

def create_flight_metrics(df: pd.DataFrame) -> None:
    """Show flight-related metrics"""
    if df.empty:
        st.warning("No transport data available.")
        return
    # Filter flights
    flight_df = df[df['type of transport'].str.lower() == "flight"]
    if flight_df.empty:
        st.info("No flight records found in transport data.")
        return
    # Metric: total flights
    st.metric("✈️ Flight Tickets", len(flight_df))
    # Table: flights from-to-price
    st.write("### ✈️ Flight Details")
    st.dataframe(
        flight_df[['from', 'to', 'price per person ( EUR )']].copy().reset_index(drop=True),
        use_container_width=True
    )
    # Total price
    total_price = flight_df['price per person ( EUR )'].sum()
    st.subheader(f"💶 Total Flight Cost: € {total_price:,.2f}")

def create_world_map(df: pd.DataFrame) -> None:
    """Creates a world map of visited countries"""
    if 'country' not in df.columns:
        st.warning("No 'country' column found in the dataset to create a map.")
        return
    country_to_iso = {
        'Afghanistan': 'AFG', 'Albania': 'ALB', 'Algeria': 'DZA', 'Andorra': 'AND', 'Angola': 'AGO',
        'Antigua and Barbuda': 'ATG', 'Argentina': 'ARG', 'Armenia': 'ARM', 'Australia': 'AUS',
        'austria': 'AUT', 'Azerbaijan': 'AZE', 'Bahamas': 'BHS', 'Bahrain': 'BHR', 'Bangladesh': 'BGD',
        'Barbados': 'BRB', 'Belarus': 'BLR', 'Belgium': 'BEL', 'Belize': 'BLZ', 'Benin': 'BEN',
        'Bhutan': 'BTN', 'Bolivia': 'BOL', 'Bosnia and Herzegovina': 'BIH', 'Botswana': 'BWA',
        'Brazil': 'BRA', 'Brunei': 'BRN', 'bulgaria': 'BGR', 'Burkina Faso': 'BFA', 'Burundi': 'BDI',
        'Cabo Verde': 'CPV', 'Cambodia': 'KHM', 'Cameroon': 'CMR', 'Canada': 'CAN',
        'Central African Republic': 'CAF', 'Chad': 'TCD', 'Chile': 'CHL', 'china': 'CHN',
        'Colombia': 'COL', 'Comoros': 'COM', 'Congo (Brazzaville)': 'COG', 'Congo (Kinshasa)': 'COD',
        'Costa Rica': 'CRI', 'Croatia': 'HRV', 'Cuba': 'CUB', 'Cyprus': 'CYP', 'Czechia': 'CZE',
        'Czech Republic': 'CZE', 'Denmark': 'DNK', 'Djibouti': 'DJI', 'Dominica': 'DMA',
        'Dominican Republic': 'DOM', 'Ecuador': 'ECU', 'Egypt': 'EGY', 'El Salvador': 'SLV',
        'Equatorial Guinea': 'GNQ', 'Eritrea': 'ERI', 'Estonia': 'EST', 'Eswatini': 'SWZ',
        'Ethiopia': 'ETH', 'Fiji': 'FJI', 'Finland': 'FIN', 'France': 'FRA', 'Gabon': 'GAB',
        'Gambia': 'GMB', 'Georgia': 'GEO', 'Germany': 'DEU', 'Ghana': 'GHA', 'Greece': 'GRC',
        'Grenada': 'GRD', 'Guatemala': 'GTM', 'Guinea': 'GIN', 'Guinea-Bissau': 'GNB', 'Guyana': 'GUY',
        'Haiti': 'HTI', 'Honduras': 'HND', 'hungary': 'HUN', 'Iceland': 'ISL', 'India': 'IND',
        'Indonesia': 'IDN', 'Iran': 'IRN', 'Iraq': 'IRQ', 'Ireland': 'IRL', 'Israel': 'ISR',
        'Italy': 'ITA', 'Jamaica': 'JAM', 'japan': 'JPN', 'Jordan': 'JOR', 'Kazakhstan': 'KAZ',
        'Kenya': 'KEN', 'Kiribati': 'KIR', 'Kuwait': 'KWT', 'Kyrgyzstan': 'KGZ', 'laos': 'LAO',
        'Latvia': 'LVA', 'Lebanon': 'LBN', 'Lesotho': 'LSO', 'Liberia': 'LBR', 'Libya': 'LBY',
        'Liechtenstein': 'LIE', 'Lithuania': 'LTU', 'Luxembourg': 'LUX', 'Madagascar': 'MDG',
        'Malawi': 'MWI', 'Malaysia': 'MYS', 'Maldives': 'MDV', 'Mali': 'MLI', 'Malta': 'MLT',
        'Marshall Islands': 'MHL', 'Mauritania': 'MRT', 'Mauritius': 'MUS', 'Mexico': 'MEX',
        'Micronesia': 'FSM', 'Moldova': 'MDA', 'Monaco': 'MCO', 'mongolia': 'MNG', 'Montenegro': 'MNE',
        'Morocco': 'MAR', 'Mozambique': 'MOZ', 'Myanmar': 'MMR', 'Namibia': 'NAM', 'Nauru': 'NRU',
        'Nepal': 'NPL', 'Netherlands': 'NLD', 'new zealand': 'NZL', 'Nicaragua': 'NIC', 'Niger': 'NER',
        'Nigeria': 'NGA', 'North Korea': 'PRK', 'North Macedonia': 'MKD', 'norway': 'NOR', 'oman': 'OMN',
        'Pakistan': 'PAK', 'Palau': 'PLW', 'Palestine': 'PSE', 'Panama': 'PAN', 'Papua New Guinea': 'PNG',
        'Paraguay': 'PRY', 'Peru': 'PER', 'Philippines': 'PHL', 'poland': 'POL', 'Portugal': 'PRT',
        'Qatar': 'QAT', 'Romania': 'ROU', 'Russia': 'RUS', 'Rwanda': 'RWA', 'Saint Kitts and Nevis': 'KNA',
        'Saint Lucia': 'LCA', 'Saint Vincent and the Grenadines': 'VCT', 'Samoa': 'WSM', 'San Marino': 'SMR',
        'Sao Tome and Principe': 'STP', 'Saudi Arabia': 'SAU', 'Senegal': 'SEN', 'Serbia': 'SRB',
        'Seychelles': 'SYC', 'Sierra Leone': 'SLE', 'Singapore': 'SGP', 'slovakia': 'SVK', 'Slovenia': 'SVN',
        'Solomon Islands': 'SLB', 'Somalia': 'SOM', 'South Africa': 'ZAF', 'south korea': 'KOR',
        'South Sudan': 'SSD', 'Spain': 'ESP', 'sri lanka': 'LKA', 'Sudan': 'SDN', 'Suriname': 'SUR',
        'sweden': 'SWE', 'Switzerland': 'CHE', 'Syria': 'SYR', 'Taiwan': 'TWN', 'Tajikistan': 'TJK',
        'Tanzania': 'TZA', 'Thailand': 'THA', 'Timor-Leste': 'TLS', 'Togo': 'TGO', 'Tonga': 'TON',
        'Trinidad and Tobago': 'TTO', 'Tunisia': 'TUN', 'turkey': 'TUR', 'Turkmenistan': 'TKM',
        'Tuvalu': 'TUV', 'Uganda': 'UGA', 'Ukraine': 'UKR', 'united arab emirates': 'ARE',
        'United Kingdom': 'GBR', 'United States': 'USA', 'USA': 'USA', 'Uruguay': 'URY',
        'Uzbekistan': 'UZB', 'Vanuatu': 'VUT', 'Vatican City': 'VAT', 'Venezuela': 'VEN',
        'Vietnam': 'VNM', 'Yemen': 'YEM', 'Zambia': 'ZMB', 'Zimbabwe': 'ZWE'
    }
    df_countries = df.dropna(subset=['country']).copy()
    df_countries['iso_alpha'] = df_countries['country'].map(country_to_iso)
    df_countries = df_countries.dropna(subset=['iso_alpha']).drop_duplicates(subset=['iso_alpha'])
    if df_countries.empty:
        st.warning("No valid countries found in the dataset for map visualization.")
        return
    df_countries['is_visited'] = 'Visited'
    fig = px.choropleth(
        df_countries,
        locations='iso_alpha',
        color='is_visited',
        title='Countries Visited',
        projection="natural earth",
        hover_name='country',
        color_discrete_map={'Visited': '#FF4B4B'}
    )
    fig.update_layout(
        geo=dict(
            bgcolor='rgba(0,0,0,0)',
            showland=True,
            landcolor="lightgrey",
            showocean=True,
            oceancolor="lightblue",
            showcountries=True,
            countrycolor="dimgrey",
            countrywidth=1,
            subunitcolor="darkgrey",
            subunitwidth=0.5
        ),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

def adjust_nights(df: pd.DataFrame) -> pd.DataFrame:
    """Adjust nights based on person column: halve nights if person is 1."""
    df_adjusted = df.copy()
    if 'person' in df_adjusted.columns:
        df_adjusted['adjusted_nights'] = df_adjusted.apply(
            lambda row: row['nights'] / 2 if pd.notna(row['person']) and row['person'] == 1 else row['nights'],
            axis=1
        )
    else:
        st.warning("Column 'person' not found. Using original nights without adjustment.")
        df_adjusted['adjusted_nights'] = df_adjusted['nights']
    return df_adjusted

def create_country_summary(df: pd.DataFrame, order_by: str = 'id') -> None:
    """Group data by country and visualize total adjusted nights and total cost."""
    if df.empty:
        st.error("The DataFrame is empty. Please provide valid data.")
        return
    required_columns = ['country', 'nights', 'total price of stay']
    if order_by == 'id':
        required_columns.append('id')
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
        return
    try:
        df['nights'] = pd.to_numeric(df['nights'], errors='coerce')
        df['total price of stay'] = pd.to_numeric(df['total price of stay'], errors='coerce')
        if order_by == 'id':
            df['id'] = pd.to_numeric(df['id'], errors='coerce')
        if 'person' in df.columns:
            df['person'] = pd.to_numeric(df['person'], errors='coerce')
    except Exception as e:
        st.error(f"Error converting columns to numeric: {str(e)}")
        return
    if df[['country', 'nights', 'total price of stay']].isna().any().any():
        st.warning("Some rows contain missing or invalid data and will be excluded.")
        df = df.dropna(subset=['country', 'nights', 'total price of stay'])
    if df.empty:
        st.error("No valid data remains after cleaning. Please check your CSV.")
        return
    df_adjusted = adjust_nights(df)
    if order_by == 'id':
        grouped_df = df_adjusted.groupby('country').agg({
            'adjusted_nights': 'sum',
            'total price of stay': 'sum',
            'id': 'first'
        }).reset_index()
        grouped_df = grouped_df.sort_values('id').drop('id', axis=1).reset_index(drop=True)
    else:
        grouped_df = df_adjusted.groupby('country').agg({
            'adjusted_nights': 'sum',
            'total price of stay': 'sum'
        }).reset_index()
    grouped_df['average_cost'] = grouped_df['total price of stay'] / grouped_df['adjusted_nights'] / 2
    paid_nights = df_adjusted[df_adjusted['total price of stay'] > 0].groupby('country')['adjusted_nights'].sum().reset_index()
    grouped_df = grouped_df.merge(paid_nights, on='country', how='left', suffixes=('', '_paid'))
    grouped_df['adjusted_nights_paid'] = grouped_df['adjusted_nights_paid'].fillna(0)
    grouped_df['avg_cost_paid_night_person'] = grouped_df.apply(
        lambda row: row['total price of stay'] / row['adjusted_nights_paid'] / 2 if row['adjusted_nights_paid'] > 0 else 0,
        axis=1
    )
    grouped_df.columns = ['Country', 'Nights', 'Total Cost (€)', 'Average Person/Night (€)', 'Paid Nights', 'Average Cost per Paid Night/Person (€)']
    grouped_df['Average Person/Night (€)'] = grouped_df['Average Person/Night (€)'].round(2)
    grouped_df['Average Cost per Paid Night/Person (€)'] = grouped_df['Average Cost per Paid Night/Person (€)'].round(2)
    st.write("### Summary by Country")
    st.dataframe(grouped_df, use_container_width=True)
    col1, col2 = st.columns(2)
    with col1:
        fig_nights = px.bar(
            grouped_df,
            x='Country',
            y='Nights',
            title='Nights by Country',
            labels={'Nights': 'Number of Nights'},
            color='Country'
        )
        fig_nights.update_layout(showlegend=False)
        st.plotly_chart(fig_nights, use_container_width=True)
    with col2:
        fig_cost = px.bar(
            grouped_df,
            x='Country',
            y='Total Cost (€)',
            title='Total Cost by Country',
            labels={'Total Cost (€)': 'Cost (€)'},
            color='Country'
        )
        fig_cost.update_layout(showlegend=False)
        st.plotly_chart(fig_cost, use_container_width=True)

def create_cost_visualization(df: pd.DataFrame) -> None:
    """Create accommodation cost visualizations"""
    cost_columns = ['total price of stay', 'cost', 'price', 'amount', 'total_cost', 'expense']
    cost_col = next((col for col in cost_columns if col in df.columns), None)
    if not cost_col:
        st.warning("No accommodation cost data found in the dataset")
        return
    col1, col2 = st.columns(2)
    with col1:
        fig_hist = px.histogram(
            df,
            x=cost_col,
            title="Distribution of Accommodation Costs",
            nbins=20,
            labels={'x': 'Cost (€)', 'y': 'Number of Stays'}
        )
        fig_hist.update_layout(showlegend=False)
        st.plotly_chart(fig_hist, use_container_width=True)
    with col2:
        date_columns = ['check in', 'check out', 'date', 'departure_date', 'arrival_date', 'booking_date', 'travel_date']
        date_col = next((col for col in date_columns if col in df.columns), None)
        if date_col:
            df_time = df.dropna(subset=[date_col, cost_col])
            if not df_time.empty:
                fig_time = px.line(
                    df_time.sort_values(date_col),
                    x=date_col,
                    y=cost_col,
                    title="Accommodation Costs Over Time",
                    labels={'x': 'Date', 'y': 'Cost (€)'}
                )
                st.plotly_chart(fig_time, use_container_width=True)
            else:
                type_columns = ['platform', 'travel_type', 'type', 'category', 'mode']
                type_col = next((col for col in type_columns if col in df.columns), None)
                if type_col:
                    fig_box = px.box(
                        df,
                        x=type_col,
                        y=cost_col,
                        title="Accommodation Costs by Booking Platform",
                        labels={'x': 'Platform', 'y': 'Cost (€)'}
                    )
                    st.plotly_chart(fig_box, use_container_width=True)

def create_destination_visualization(df: pd.DataFrame) -> None:
    """Pie chart: Top 10 countries by nights spent"""
    if "country" not in df.columns or "nights" not in df.columns:
        st.warning("Dataset must have 'country' and 'nights' columns")
        return
    country_nights = df.groupby("country")["nights"].sum().nlargest(10)
    fig_pie = px.pie(
        values=country_nights.values,
        names=country_nights.index,
        title="🌍 Top 10 Countries by Nights Spent"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

def create_accommodation_patterns_visualization(df: pd.DataFrame) -> None:
    """Create accommodation booking pattern visualizations"""
    date_columns = ['check in', 'check out', 'date', 'departure_date', 'arrival_date', 'booking_date', 'travel_date']
    date_col = next((col for col in date_columns if col in df.columns), None)
    if not date_col:
        st.warning("No date data found for accommodation patterns analysis")
        return
    df_clean = df.dropna(subset=[date_col])
    if df_clean.empty:
        st.warning("No valid date data available")
        return
    col1, col2 = st.columns(2)
    with col1:
        df_clean['month'] = df_clean[date_col].dt.month_name()
        monthly_counts = df_clean['month'].value_counts()
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        monthly_counts = monthly_counts.reindex([m for m in month_order if m in monthly_counts.index])
        fig_monthly = px.bar(
            x=monthly_counts.index,
            y=monthly_counts.values,
            title="Accommodation Bookings by Month",
            labels={'x': 'Month', 'y': 'Number of Stays'}
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
    with col2:
        df_clean['day_of_week'] = df_clean[date_col].dt.day_name()
        dow_counts = df_clean['day_of_week'].value_counts()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_counts = dow_counts.reindex([d for d in day_order if d in dow_counts.index])
        fig_dow = px.bar(
            x=dow_counts.index,
            y=dow_counts.values,
            title="Check-in Frequency by Day of Week",
            labels={'x': 'Day of Week', 'y': 'Number of Stays'}
        )
        st.plotly_chart(fig_dow, use_container_width=True)

def main() -> None:
    """Main application function"""
    st.title("🏨 Tam Vonku Dashboard")
    st.markdown("---")
    df = load_data()
    if df.empty:
        st.warning("No data available. Please ensure travel_data.csv exists and contains valid accommodation data.")
        st.stop()
    st.sidebar.header("🔍 Filters")
    date_columns = ['check in', 'check out', 'date', 'departure_date', 'arrival_date', 'booking_date', 'travel_date']
    date_col = next((col for col in date_columns if col in df.columns), None)
    if date_col:
        df_clean_dates = df.dropna(subset=[date_col])
        if not df_clean_dates.empty:
            min_date = df_clean_dates[date_col].min().date()
            max_date = df_clean_dates[date_col].max().date()
            selected_dates = st.sidebar.date_input(
                "Select Check-in Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            if len(selected_dates) == 2:
                start_date, end_date = selected_dates
                df = df[(df[date_col].dt.date >= start_date) & (df[date_col].dt.date <= end_date)]
    st.sidebar.header("🔍 Filter by Country")
    if "country" in df.columns:
        countries = df["country"].dropna().unique()
        selected_countries = st.sidebar.multiselect(
            "Select Country(s)",
            options=sorted(countries),
            default=sorted(countries)
        )
        if selected_countries:
            df = df[df["country"].isin(selected_countries)]
    else:
        st.sidebar.warning("No 'country' column found in the dataset.")
    st.header("📊 Summary Statistics")
    metrics = create_summary_metrics(df)
    if metrics:
        if 'days_on_road' in metrics:
            st.metric("🗓️ Days on the Road", f"{metrics['days_on_road']:,} days", help="Total duration from first check-in to last check-out")
            st.markdown("---")
        other_metrics = {k: v for k, v in metrics.items() if k != 'days_on_road'}
        if other_metrics:
            cols = st.columns(len(other_metrics))
            for i, (key, value) in enumerate(other_metrics.items()):
                with cols[i % len(cols)]:
                    if isinstance(value, (int, float)) and key.endswith('cost'):
                        st.metric(key.replace('_', ' ').title(), f"€{value:,.2f}")
                    elif isinstance(value, (int, float)):
                        st.metric(key.replace('_', ' ').title(), f"{value:,}")
                    else:
                        st.metric(key.replace('_', ' ').title(), str(value))
            st.markdown("---")
    st.header("✈️ Flight Statistics")
    df_transport = load_transport_data()
    create_flight_metrics(df_transport)
    st.markdown("---")
    st.header("🌍 World Map of Visited Countries")
    create_world_map(df)
    st.markdown("---")
    if not df.empty:
        st.header("💰 Accommodation Cost Analysis")
        create_country_summary(df, order_by='id')
        st.markdown("---")
        st.header("🌍 Time Spent by Country")
        create_destination_visualization(df)
        st.markdown("---")
        st.header("📋 Raw Data")
        st.dataframe(df, use_container_width=True)
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv_data,
            file_name=f"filtered_accommodation_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data matches the selected filters.")

if __name__ == "__main__":
    main()
