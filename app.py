import streamlit as st
import pandas as pd
import plotly.express as px

# --- APP CONFIGURATION ---
st.set_page_config(page_title="System Calibration Dashboard", layout="wide")

# --- HEADER & ONBOARDING ---
st.title("🛡️ System Calibration Log")
with st.expander("ℹ️ How this app works & Your Privacy"):
    st.write("""
    **Privacy:** Your data is never stored here. It lives in your personal Google Drive.
    **Data Entry:** Use your Google Sheet to log entries. This dashboard summarizes your progress by day.
    """)

# --- SIDEBAR ---
st.sidebar.header("Connection")
raw_url = st.sidebar.text_input("Paste Google Sheet URL here:")

if raw_url:
    try:
        clean_url = raw_url.strip()
        sheet_id = clean_url.split("/d/")[1].split("/")[0]
        base_query = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
        
        # Load Data
        df_cal = pd.read_csv(f"{base_query}&sheet=Calibration%20Log")
        df_duty = pd.read_csv(f"{base_query}&sheet=Duty%20Cycle")

        # CRITICAL FIX: Strip time and force to Date format
        df_cal['Date'] = pd.to_datetime(df_cal['Date']).dt.date
        df_duty['Date'] = pd.to_datetime(df_duty['Date']).dt.date

        # --- CHART 1: CLEAN DAILY VOLUME ---
        st.subheader("Daily Volume Trend (Wet Weight)")
        # Summing all weights for each unique date
        daily_vol = df_cal.groupby('Date')['Wet Weight (g)'].sum().reset_index()
        daily_vol['7-Day Avg'] = daily_vol['Wet Weight (g)'].rolling(window=7, min_periods=1).mean()
        
        fig1 = px.bar(daily_vol, x='Date', y='Wet Weight (g)', 
                     title="Total Daily Leakage (ml)",
                     color_discrete_sequence=['lightgray'])
        fig1.add_scatter(x=daily_vol['Date'], y=daily_vol['7-Day Avg'], name='7-Day Avg', line=dict(color='red', width=3))
        # Force X-axis to show dates only
        fig1.update_xaxes(type='category', tickformat='%b %d')
        st.plotly_chart(fig1, use_container_width=True)

        # --- CHART 2: CLEAN TANK CAPACITY ---
        st.subheader("Operational Capacity (The Tank)")
        # Show the MAXIMUM (Best) interval achieved each day
        daily_max_dry = df_duty.groupby('Date')['Dry Duration (min)'].max().reset_index()
        
        fig2 = px.bar(daily_max_dry, x='Date', y='Dry Duration (min)',
                     title="Longest Dry Interval per Day (Minutes)",
                     color_discrete_sequence=['#00CC96'])
        fig2.update_xaxes(type='category', tickformat='%b %d')
        st.plotly_chart(fig2, use_container_width=True)

        # --- CHART 3: FAILURE MODE ---
        st.subheader("Root Cause Analysis")
        triggers = {
            'Pressure [P]': df_cal['Pressure Failure (P)'].sum(),
            'Volume [V]': df_cal['Vol. Failure (V)'].sum(),
            'Fatigue [F]': df_cal['Fatigue Failure (F)'].sum()
        }
        fig3 = px.pie(names=list(triggers.keys()), values=list(triggers.values()), hole=0.4)
        st.plotly_chart(fig3, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("👆 Paste your Google Sheet URL in the sidebar.")
