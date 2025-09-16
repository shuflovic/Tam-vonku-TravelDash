# 🏨 Tam Vonku Dashboard

Tam Vonku Dashboard is an **interactive Streamlit web application** for analyzing and visualizing travel and accommodation data.  
It helps track trips, costs, visited countries, accommodation patterns, Workaway projects, and transport (including flights).  

---

## ✨ Features

- **Data Loading & Cleaning**
  - Reads from `travel_data.csv` (accommodation stays) and `data_transport.csv` (transport)
  - Cleans European-style numbers (commas, spaces)
  - Converts date columns to `datetime`
  - Creates combined `destination` field (city + country)

- **Summary Statistics**
  - Total **days on the road**
  - Number of **unique places stayed**
  - Number of **visited countries**
  - **Total accommodation costs** and **average per person per night**
  - Count of **Workaway projects**
  - Most frequent (top) destination

- **Transport Analysis**
  - Flight metrics:
    - Count of tickets
    - Table with flight details (`from`, `to`, `price`)
    - Total flight costs

- **World Map**
  - Choropleth world map of visited countries

- **Accommodation & Cost Analysis**
  - Summary by country:
    - Nights, costs, averages per person/night
    - Distinction between **paid vs unpaid nights**
  - Histograms, line charts, and boxplots for accommodation costs
  - Time-based analysis of bookings
  - Visualizations of seasonal and weekly booking patterns

- **Workaway Projects**
  - Shows Workaway stays separately
  - Aggregates by country & accommodation
  - Adds a total nights summary row
  - Includes bar chart of nights per accommodation

- **Interactive Filters**
  - Filter by date range
  - Filter by selected country/countries

- **Export**
  - Download filtered data as CSV

---

## 📂 Input Data

The app expects two CSV files in the project root:

### 1. `travel_data.csv`
Must contain some of these columns:

| check in | check out | country | location | accommodation | nights | person | platform | total price of stay | id |
|----------|-----------|---------|----------|---------------|--------|--------|----------|---------------------|----|

### 2. `data_transport.csv`
Transport details with columns like:

| date       | type of transport | from | to | price per person ( EUR ) |
|------------|------------------|------|----|--------------------------|
| 2024-05-01 | Flight           | LON  | BCN | 120.5                    |

---
