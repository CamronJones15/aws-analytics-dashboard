"""
dashboard/app.py

Streamlit analytics dashboard for NYC Taxi trip data.
Queries AWS Athena and renders charts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.queries import run_query, TRIPS_BY_DAY, TRIPS_BY_HOUR, TOP_ZONES

st.set_page_config(
    page_title="NYC Taxi Analytics",
    page_icon="🚕",
    layout="wide",
)

st.title("🚕 NYC Taxi Analytics Dashboard")
st.caption("Powered by AWS Athena + S3 · Data: NYC TLC")

# --- Sidebar ---
st.sidebar.header("Filters")
year = st.sidebar.selectbox("Year", [2024, 2023], index=0)
month = st.sidebar.selectbox("Month", list(range(1, 13)), index=0)

if st.sidebar.button("Refresh Data"):
    st.cache_data.clear()


@st.cache_data(ttl=3600)
def load_trips_by_day():
    return run_query(TRIPS_BY_DAY)


@st.cache_data(ttl=3600)
def load_trips_by_hour():
    return run_query(TRIPS_BY_HOUR)


@st.cache_data(ttl=3600)
def load_top_zones():
    return run_query(TOP_ZONES)


# --- KPI Row ---
with st.spinner("Loading data from Athena..."):
    df_day = load_trips_by_day()
    df_hour = load_trips_by_hour()
    df_zones = load_top_zones()

df_day["trip_count"] = pd.to_numeric(df_day["trip_count"])
df_day["avg_fare"] = pd.to_numeric(df_day["avg_fare"])
df_hour["trip_count"] = pd.to_numeric(df_hour["trip_count"])

col1, col2, col3 = st.columns(3)
col1.metric("Total Trips", f"{df_day['trip_count'].sum():,.0f}")
col2.metric("Avg Fare", f"${df_day['avg_fare'].mean():.2f}")
col3.metric("Days Covered", f"{len(df_day)}")

st.divider()

# --- Charts ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Daily Trip Volume")
    fig = px.bar(df_day, x="pickup_date", y="trip_count", color_discrete_sequence=["#F6C90E"])
    fig.update_layout(xaxis_title="Date", yaxis_title="Trips", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Trips by Hour of Day")
    df_hour["pickup_hour"] = pd.to_numeric(df_hour["pickup_hour"])
    fig2 = px.line(df_hour, x="pickup_hour", y="trip_count", markers=True,
                   color_discrete_sequence=["#2196F3"])
    fig2.update_layout(xaxis_title="Hour", yaxis_title="Trips", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Top 10 Pickup Zones")
df_zones["pickups"] = pd.to_numeric(df_zones["pickups"])
fig3 = px.bar(df_zones, x="zone_id", y="pickups", color_discrete_sequence=["#4CAF50"])
fig3.update_layout(xaxis_title="Zone ID", yaxis_title="Pickups", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig3, use_container_width=True)

st.caption("Data refreshes every hour. Source: NYC TLC Trip Record Data.")
