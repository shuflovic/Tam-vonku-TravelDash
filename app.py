import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import os
from typing import Dict, Any, Optional

# Page configuration
st.set_page_config(
    page_title="Travel Data Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and cache the travel data"""
    try:
        if os.path.exists("travel_data.csv"):
            df = pd.read_csv("travel_data.csv")
            
            # Convert date columns to datetime if they exist
            date_columns = ['date', 'departure_date', 'arrival_date', 'booking_date', 'travel_date']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
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
    
    # Basic metrics
    metrics['total_trips'] = len(df)
    
    # Cost metrics if cost column exists
    cost_columns = ['cost', 'price', 'amount', 'total_cost', 'expense']
    cost_col = None
    for col in cost_columns:
        if col in df.columns:
            cost_col = col
            break
    
    if cost_col:
        metrics['total_cost'] = df[cost_col].sum()
        metrics['avg_cost'] = df[cost_col].mean()
        metrics['max_cost'] = df[cost_col].max()
        metrics['min_cost'] = df[cost_col].min()
    
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
    
    # Travel type metrics
    type_columns = ['travel_type', 'type', 'category', 'mode']
    type_col = None
    for col in type_columns:
        if col in df.columns:
            type_col = col
            break
    
    if type_col:
        metrics['travel_types'] = df[type_col].nunique()
    
    return metrics

def create_cost_visualization(df: pd.DataFrame) -> None:
    """Create cost-related visualizations"""
    cost_columns = ['cost', 'price', 'amount', 'total_cost', 'expense']
    cost_col = None
    for col in cost_columns:
        if col in df.columns:
            cost_col = col
            break
    
    if not cost_col:
        st.warning("No cost data found in the dataset")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Cost distribution histogram
        fig_hist = px.histogram(
            df, 
            x=cost_col, 
            title=f"Distribution of {cost_col.title()}",
            nbins=20
        )
        fig_hist.update_layout(showlegend=False)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Cost over time if date column exists
        date_columns = ['date', 'departure_date', 'arrival_date', 'booking_date', 'travel_date']
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
                    title=f"{cost_col.title()} Over Time"
                )
                st.plotly_chart(fig_time, use_container_width=True)
        else:
            # Box plot by travel type if available
            type_columns = ['travel_type', 'type', 'category', 'mode']
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
                    title=f"{cost_col.title()} by {type_col.title()}"
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
            labels={'x': dest_col.title(), 'y': 'Number of Trips'}
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

def create_travel_patterns_visualization(df: pd.DataFrame) -> None:
    """Create travel pattern visualizations"""
    date_columns = ['date', 'departure_date', 'arrival_date', 'booking_date', 'travel_date']
    date_col = None
    for col in date_columns:
        if col in df.columns:
            date_col = col
            break
    
    if not date_col:
        st.warning("No date data found for travel patterns analysis")
        return
    
    df_clean = df.dropna(subset=[date_col])
    if df_clean.empty:
        st.warning("No valid date data available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly travel frequency
        df_clean['month'] = df_clean[date_col].dt.month_name()
        monthly_counts = df_clean['month'].value_counts()
        
        # Reorder by calendar month
        month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        monthly_counts = monthly_counts.reindex([m for m in month_order if m in monthly_counts.index])
        
        fig_monthly = px.bar(
            x=monthly_counts.index,
            y=monthly_counts.values,
            title="Travel Frequency by Month",
            labels={'x': 'Month', 'y': 'Number of Trips'}
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    with col2:
        # Day of week analysis
        df_clean['day_of_week'] = df_clean[date_col].dt.day_name()
        dow_counts = df_clean['day_of_week'].value_counts()
        
        # Reorder by weekday
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_counts = dow_counts.reindex([d for d in day_order if d in dow_counts.index])
        
        fig_dow = px.bar(
            x=dow_counts.index,
            y=dow_counts.values,
            title="Travel Frequency by Day of Week",
            labels={'x': 'Day of Week', 'y': 'Number of Trips'}
        )
        st.plotly_chart(fig_dow, use_container_width=True)

def main() -> None:
    """Main application function"""
    st.title("✈️ Travel Data Dashboard")
    st.markdown("---")
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.warning("No data available. Please ensure travel_data.csv exists and contains valid data.")
        st.stop()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Date range filter
    date_columns = ['date', 'departure_date', 'arrival_date', 'booking_date', 'travel_date']
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
                "Select Date Range",
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
    
    # Travel type filter
    type_columns = ['travel_type', 'type', 'category', 'mode']
    type_col = None
    for col in type_columns:
        if col in df.columns:
            type_col = col
            break
    
    if type_col:
        travel_types = df[type_col].dropna().unique()
        selected_types = st.sidebar.multiselect(
            f"Select {type_col.title()}(s)",
            options=travel_types,
            default=travel_types
        )
        if selected_types:
            df = df[df[type_col].isin(selected_types)]
    
    # Summary metrics
    st.header("📊 Summary Statistics")
    metrics = create_summary_metrics(df)
    
    if metrics:
        cols = st.columns(len(metrics))
        for i, (key, value) in enumerate(metrics.items()):
            with cols[i % len(cols)]:
                if isinstance(value, (int, float)) and key.endswith('cost'):
                    st.metric(key.replace('_', ' ').title(), f"${value:,.2f}")
                elif isinstance(value, (int, float)):
                    st.metric(key.replace('_', ' ').title(), f"{value:,}")
                else:
                    st.metric(key.replace('_', ' ').title(), str(value))
    
    st.markdown("---")
    
    # Visualizations
    if not df.empty:
        # Cost Analysis
        st.header("💰 Cost Analysis")
        create_cost_visualization(df)
        
        st.markdown("---")
        
        # Destination Analysis
        st.header("🌍 Destination Analysis")
        create_destination_visualization(df)
        
        st.markdown("---")
        
        # Travel Patterns
        st.header("📈 Travel Patterns")
        create_travel_patterns_visualization(df)
        
        st.markdown("---")
        
        # Data table
        st.header("📋 Raw Data")
        st.dataframe(df, width='stretch')
        
        # Download filtered data
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv_data,
            file_name=f"filtered_travel_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data matches the selected filters.")

if __name__ == "__main__":
    main()
