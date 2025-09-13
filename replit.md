# Travel Data Dashboard

## Overview

This project is a Streamlit-based web application for visualizing and analyzing travel data. The dashboard provides interactive data visualization capabilities using Plotly charts and pandas for data manipulation. The application is designed to load travel data from a CSV file and display comprehensive analytics through a user-friendly web interface.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - chosen for rapid development of data applications with minimal frontend code
- **Visualization**: Plotly Express and Plotly Graph Objects for interactive charts and graphs
- **Layout**: Wide layout with expandable sidebar for optimal data visualization experience
- **Caching**: Streamlit's @st.cache_data decorator for performance optimization of data loading operations

### Data Processing Layer
- **Data Manipulation**: Pandas for data processing, cleaning, and transformation
- **Numerical Operations**: NumPy for mathematical computations and array operations
- **Date Handling**: Python datetime module with automatic date column detection and conversion

### Data Storage
- **Primary Storage**: CSV file-based storage (travel_data.csv)
- **Data Schema**: Flexible schema supporting multiple date column formats (date, departure_date, arrival_date, booking_date, travel_date)
- **Cost Data**: Support for various cost column names (cost, price, amount, total_cost, expense)

### Application Structure
- **Single-file Architecture**: Monolithic app.py structure for simplicity
- **Error Handling**: Comprehensive exception handling for data loading and processing
- **Configuration**: Centralized page configuration with travel theme (✈️ icon)

### Performance Optimizations
- **Data Caching**: Streamlit caching mechanism to prevent redundant data loading
- **Lazy Loading**: Data is only processed when the CSV file exists
- **Error Recovery**: Graceful degradation when data files are missing or corrupted

## External Dependencies

### Python Libraries
- **streamlit**: Web application framework for the dashboard interface
- **pandas**: Data manipulation and analysis library
- **plotly**: Interactive visualization library (both express and graph_objects modules)
- **numpy**: Numerical computing library for mathematical operations

### Data Dependencies
- **travel_data.csv**: Primary data source file expected in the project root directory
- **File System**: Local file system access for CSV data loading

### Runtime Environment
- **Python Environment**: Requires Python with the specified dependencies installed
- **Streamlit Server**: Built-in Streamlit server for hosting the web application