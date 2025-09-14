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

            # Handle European number format in cost column (spaces as thousands separator, comma as decimal)
            if 'total price of stay' in df.columns:
                df['total price of stay'] = df['total price of stay'].astype(str).str.replace(' ', '').str.replace(',', '.').astype(float)

            # Convert date columns to datetime
            date_columns = ['check in', 'check out']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], format='%d.%m.%Y', errors='coerce')

            # Create a combined destination column
            if 'country' in df.columns and 'location' in df.columns:
                df['destination'] = df['location'].astype(str) + ', ' + df['country'].astype(str)

            return df
        else:
            st.error("travel_data.csv file not found in the project directory. Please ensure the file exists.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def create_summary_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Create summary statistics for the dashboard"""
    if df.empty:
        return {}

    metrics = {}

    # Days on the Road - total trip duration
    if 'check in' in df.columns and 'check out' in df.columns:
        df_dates = df.dropna(subset=['check in', 'check out'])
        if not df_dates.empty:
            first_day = df_dates['check in'].min()
            last_day = df_dates['check out'].max()
            if pd.notna(first_day) and pd.notna(last_day):
                total_days = (last_day - first_day).days + 1
                metrics['days_on_road'] = total_days

    # Basic metrics
    metrics['total_stays'] = df['accommodation'].nunique()

    # Add the new metric for unique countries visited
    if 'country' in df.columns:
        metrics['total_countries_visited'] = df['country'].nunique()

    # Cost metrics if cost column exists
    cost_columns = ['total price of stay', 'cost', 'price', 'amount', 'total_cost', 'expense']
    cost_col = None
    for col in cost_columns:
        if col in df.columns:
            cost_col = col
            break

    if cost_col:
        metrics['total_cost'] = df[cost_col].sum()
   #     metrics['avg_cost'] = df[cost_col].mean()
        metrics['average per peron per night'] = df[cost_col].sum() / 2 / metrics['days_on_road']
   #     metrics['max_cost'] = df[cost_col].max()
   #     metrics['min_cost'] = df[cost_col].min()

    # Destination metrics
    destination_columns = ['destination', 'city', 'country', 'location']
    dest_col = None
    for col in destination_columns:
        if col in df.columns:
            dest_col = col
            break

    if dest_col:
        metrics['unique_destinations'] = df[dest_col].nunique()
        metrics['top_destination'] = df[dest_col].value_counts().index[0] if not df[dest_col].value_counts().empty else "N/A"

    # Platform metrics (accommodation booking platform)
    type_columns = ['platform', 'travel_type', 'type', 'category', 'mode']
    type_col = None
    for col in type_columns:
        if col in df.columns:
            type_col = col
            break

    if type_col:
        # Get the number of unique booking platforms
        metrics['booking_platforms'] = df[type_col].nunique()

        # Count the number of unique Workaway projects
        # This is the new logic based on your request
        if 'accommodation' in df.columns:
            workaway_projects = df[df[type_col].str.lower() == 'workaway']['accommodation'].nunique()
            metrics['unique_workaway_projects'] = workaway_projects

    return metrics

    return metrics

def create_world_map(df: pd.DataFrame) -> None:
    """Creates a world map of visited countries"""
    if 'country' not in df.columns:
        st.warning("No 'country' column found in the dataset to create a map.")
        return

    # A more comprehensive mapping of common country names to ISO alpha-3 codes
    country_to_iso = {
        'Afghanistan': 'AFG', 'Albania': 'ALB', 'Algeria': 'DZA', 'Andorra': 'AND', 'Angola': 'AGO',
        'Antigua and Barbuda': 'ATG', 'Argentina': 'ARG', 'Armenia': 'ARM', 'Australia': 'AUS', 'austria': 'AUT',
        'Azerbaijan': 'AZE', 'Bahamas': 'BHS', 'Bahrain': 'BHR', 'Bangladesh': 'BGD', 'Barbados': 'BRB',
        'Belarus': 'BLR', 'Belgium': 'BEL', 'Belize': 'BLZ', 'Benin': 'BEN', 'Bhutan': 'BTN', 'Bolivia': 'BOL',
        'Bosnia and Herzegovina': 'BIH', 'Botswana': 'BWA', 'Brazil': 'BRA', 'Brunei': 'BRN', 'bulgaria': 'BGR',
        'Burkina Faso': 'BFA', 'Burundi': 'BDI', 'Cabo Verde': 'CPV', 'Cambodia': 'KHM', 'Cameroon': 'CMR',
        'Canada': 'CAN', 'Central African Republic': 'CAF', 'Chad': 'TCD', 'Chile': 'CHL', 'china': 'CHN',
        'Colombia': 'COL', 'Comoros': 'COM', 'Congo (Brazzaville)': 'COG', 'Congo (Kinshasa)': 'COD', 'Costa Rica': 'CRI',
        'Croatia': 'HRV', 'Cuba': 'CUB', 'Cyprus': 'CYP', 'Czechia': 'CZE', 'Czech Republic': 'CZE',
        'Denmark': 'DNK', 'Djibouti': 'DJI', 'Dominica': 'DMA', 'Dominican Republic': 'DOM', 'Ecuador': 'ECU',
        'Egypt': 'EGY', 'El Salvador': 'SLV', 'Equatorial Guinea': 'GNQ', 'Eritrea': 'ERI', 'Estonia': 'EST',
        'Eswatini': 'SWZ', 'Ethiopia': 'ETH', 'Fiji': 'FJI', 'Finland': 'FIN', 'France': 'FRA', 'Gabon': 'GAB',
        'Gambia': 'GMB', 'Georgia': 'GEO', 'Germany': 'DEU', 'Ghana': 'GHA', 'Greece': 'GRC', 'Grenada': 'GRD',
        'Guatemala': 'GTM', 'Guinea': 'GIN', 'Guinea-Bissau': 'GNB', 'Guyana': 'GUY', 'Haiti': 'HTI',
        'Honduras': 'HND', 'hungary': 'HUN', 'Iceland': 'ISL', 'India': 'IND', 'Indonesia': 'IDN', 'Iran': 'IRN',
        'Iraq': 'IRQ', 'Ireland': 'IRL', 'Israel': 'ISR', 'Italy': 'ITA', 'Jamaica': 'JAM', 'japan': 'JPN',
        'Jordan': 'JOR', 'Kazakhstan': 'KAZ', 'Kenya': 'KEN', 'Kiribati': 'KIR', 'Kuwait': 'KWT', 'Kyrgyzstan': 'KGZ',
        'laos': 'LAO', 'Latvia': 'LVA', 'Lebanon': 'LBN', 'Lesotho': 'LSO', 'Liberia': 'LBR', 'Libya': 'LBY',
        'Liechtenstein': 'LIE', 'Lithuania': 'LTU', 'Luxembourg': 'LUX', 'Madagascar': 'MDG', 'Malawi': 'MWI',
        'Malaysia': 'MYS', 'Maldives': 'MDV', 'Mali': 'MLI', 'Malta': 'MLT', 'Marshall Islands': 'MHL',
        'Mauritania': 'MRT', 'Mauritius': 'MUS', 'Mexico': 'MEX', 'Micronesia': 'FSM', 'Moldova': 'MDA',
        'Monaco': 'MCO', 'mongolia': 'MNG', 'Montenegro': 'MNE', 'Morocco': 'MAR', 'Mozambique': 'MOZ',
        'Myanmar': 'MMR', 'Namibia': 'NAM', 'Nauru': 'NRU', 'Nepal': 'NPL', 'Netherlands': 'NLD', 'new zealand': 'NZL',
        'Nicaragua': 'NIC', 'Niger': 'NER', 'Nigeria': 'NGA', 'North Korea': 'PRK', 'North Macedonia': 'MKD',
        'norway': 'NOR', 'oman': 'OMN', 'Pakistan': 'PAK', 'Palau': 'PLW', 'Palestine': 'PSE', 'Panama': 'PAN',
        'Papua New Guinea': 'PNG', 'Paraguay': 'PRY', 'Peru': 'PER', 'Philippines': 'PHL', 'poland': 'POL',
        'Portugal': 'PRT', 'Qatar': 'QAT', 'Romania': 'ROU', 'Russia': 'RUS', 'Rwanda': 'RWA',
        'Saint Kitts and Nevis': 'KNA', 'Saint Lucia': 'LCA', 'Saint Vincent and the Grenadines': 'VCT', 'Samoa': 'WSM', 'San Marino': 'SMR',
        'Sao Tome and Principe': 'STP', 'Saudi Arabia': 'SAU', 'Senegal': 'SEN', 'Serbia': 'SRB', 'Seychelles': 'SYC',
        'Sierra Leone': 'SLE', 'Singapore': 'SGP', 'slovakia': 'SVK', 'Slovenia': 'SVN', 'Solomon Islands': 'SLB',
        'Somalia': 'SOM', 'South Africa': 'ZAF', 'south korea': 'KOR', 'South Sudan': 'SSD', 'Spain': 'ESP',
        'sri lanka': 'LKA', 'Sudan': 'SDN', 'Suriname': 'SUR', 'sweden': 'SWE', 'Switzerland': 'CHE',
        'Syria': 'SYR', 'Taiwan': 'TWN', 'Tajikistan': 'TJK', 'Tanzania': 'TZA', 'Thailand': 'THA', 'Timor-Leste': 'TLS',
        'Togo': 'TGO', 'Tonga': 'TON', 'Trinidad and Tobago': 'TTO', 'Tunisia': 'TUN', 'turkey': 'TUR',
        'Turkmenistan': 'TKM', 'Tuvalu': 'TUV', 'Uganda': 'UGA', 'Ukraine': 'UKR', 'united arab emirates': 'ARE',
        'United Kingdom': 'GBR', 'United States': 'USA', 'USA': 'USA', 'Uruguay': 'URY', 'Uzbekistan': 'UZB', 'Vanuatu': 'VUT',
        'Vatican City': 'VAT', 'Venezuela': 'VEN', 'Vietnam': 'VNM', 'Yemen': 'YEM', 'Zambia': 'ZMB', 'Zimbabwe': 'ZWE'
    }

    df_countries = df.dropna(subset=['country']).copy()
    df_countries['iso_alpha'] = df_countries['country'].map(country_to_iso)
    df_countries = df_countries.dropna(subset=['iso_alpha']).drop_duplicates(subset=['iso_alpha'])

    if df_countries.empty:
        st.warning("No valid countries found in the dataset for map visualization.")
        return

    # Create a new column to mark countries as 'visited'
    df_countries['is_visited'] = 'Visited'

    fig = px.choropleth(
        df_countries,
        locations='iso_alpha',
        color='is_visited',
        title='Countries Visited',
        projection="natural earth",
        hover_name='country',
        color_discrete_map={'Visited': '#FF4B4B'}  # Use a vibrant red color
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


def create_cost_visualization(df: pd.DataFrame) -> None:
    """Create accommodation cost visualizations"""
    cost_columns = ['total price of stay', 'cost', 'price', 'amount', 'total_cost', 'expense']
    cost_col = None
    for col in cost_columns:
        if col in df.columns:
            cost_col = col
            break

    if not cost_col:
        st.warning("No accommodation cost data found in the dataset")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Cost distribution histogram
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
        # Cost over time if date column exists
        date_columns = ['check in', 'check out', 'date', 'departure_date', 'arrival_date', 'booking_date', 'travel_date']
        date_col = None
        for col in date_columns:
            if col in df.columns:
                date_col = col
                break

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
            # Box plot by booking platform if available
            type_columns = ['platform', 'travel_type', 'type', 'category', 'mode']
            type_col = None
            for col in type_columns:
                if col in df.columns:
                    type_col = col
                    break

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
    """Create destination-related visualizations"""
    destination_columns = ['destination', 'city', 'country', 'location']
    dest_col = None
    for col in destination_columns:
        if col in df.columns:
            dest_col = col
            break

    if not dest_col:
        st.warning("No destination data found in the dataset")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Top destinations bar chart
        dest_counts = df[dest_col].value_counts().head(10)
        fig_bar = px.bar(
            x=dest_counts.index,
            y=dest_counts.values,
            title=f"Top 10 {dest_col.title()}s",
            labels={'x': dest_col.title(), 'y': 'Number of Stays'}
        )
        fig_bar.update_xaxes(tickangle=45)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        # Destination pie chart
        dest_counts_pie = df[dest_col].value_counts().head(8)
        fig_pie = px.pie(
            values=dest_counts_pie.values,
            names=dest_counts_pie.index,
            title=f"{dest_col.title()} Distribution"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

def create_accommodation_patterns_visualization(df: pd.DataFrame) -> None:
    """Create accommodation booking pattern visualizations"""
    date_columns = ['check in', 'check out', 'date', 'departure_date', 'arrival_date', 'booking_date', 'travel_date']
    date_col = None
    for col in date_columns:
        if col in df.columns:
            date_col = col
            break

    if not date_col:
        st.warning("No date data found for accommodation patterns analysis")
        return

    df_clean = df.dropna(subset=[date_col])
    if df_clean.empty:
        st.warning("No valid date data available")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Monthly accommodation bookings
        df_clean['month'] = df_clean[date_col].dt.month_name()
        monthly_counts = df_clean['month'].value_counts()

        # Reorder by calendar month
        month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December']
        monthly_counts = monthly_counts.reindex([m for m in month_order if m in monthly_counts.index])

        fig_monthly = px.bar(
            x=monthly_counts.index,
            y=monthly_counts.values,
            title="Accommodation Bookings by Month",
            labels={'x': 'Month', 'y': 'Number of Stays'}
        )
        st.plotly_chart(fig_monthly, use_container_width=True)

    with col2:
        # Day of week booking analysis
        df_clean['day_of_week'] = df_clean[date_col].dt.day_name()
        dow_counts = df_clean['day_of_week'].value_counts()

        # Reorder by weekday
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

    # Load data
    df = load_data()

    if df.empty:
        st.warning("No data available. Please ensure travel_data.csv exists and contains valid accommodation data.")
        st.stop()

    # Sidebar filters
    st.sidebar.header("🔍 Filters")

    # Date range filter
    date_columns = ['check in', 'check out', 'date', 'departure_date', 'arrival_date', 'booking_date', 'travel_date']
    date_col = None
    for col in date_columns:
        if col in df.columns:
            date_col = col
            break

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
                df = df[
                    (df[date_col].dt.date >= start_date) & 
                    (df[date_col].dt.date <= end_date)
                ]

    # Destination filter
    destination_columns = ['destination', 'city', 'country', 'location']
    dest_col = None
    for col in destination_columns:
        if col in df.columns:
            dest_col = col
            break

    if dest_col:
        destinations = df[dest_col].dropna().unique()
        selected_destinations = st.sidebar.multiselect(
            f"Select {dest_col.title()}(s)",
            options=destinations,
            default=destinations
        )
        if selected_destinations:
            df = df[df[dest_col].isin(selected_destinations)]

    # Booking platform filter
    type_columns = ['platform', 'travel_type', 'type', 'category', 'mode']
    type_col = None
    for col in type_columns:
        if col in df.columns:
            type_col = col
            break

    if type_col:
        platforms = df[type_col].dropna().unique()
        selected_platforms = st.sidebar.multiselect(
            "Select Booking Platform(s)",
            options=platforms,
            default=platforms
        )
        if selected_platforms:
            df = df[df[type_col].isin(selected_platforms)]

    # Summary metrics
    st.header("📊 Summary Statistics")
    metrics = create_summary_metrics(df)

    if metrics:
        # Show Days on the Road prominently first if available
        if 'days_on_road' in metrics:
            st.metric("🗓️ Days on the Road", f"{metrics['days_on_road']:,} days", help="Total duration from first check-in to last check-out")
            st.markdown("---")

        # Display other metrics in columns
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

    # Add the new world map visualization
    st.header("🌍 World Map of Visited Countries")
    create_world_map(df)

    st.markdown("---")

    # Visualizations
    if not df.empty:
        # Accommodation Cost Analysis
        st.header("💰 Accommodation Cost Analysis")
        create_cost_visualization(df)

        st.markdown("---")

        # Location Analysis
        st.header("🌍 Accommodation Locations")
        create_destination_visualization(df)

        st.markdown("---")

        # Booking Patterns
        st.header("📈 Booking Patterns")
        create_accommodation_patterns_visualization(df)

        st.markdown("---")

        # Data table
        st.header("📋 Raw Data")
        st.dataframe(df, width='stretch')

        # Download filtered data
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
