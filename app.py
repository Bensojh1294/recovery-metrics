import streamlit as st
import pandas as pd
import plotly.express as px

# --- APP CONFIGURATION ---
st.set_page_config(page_title="System Calibration Dashboard", layout="wide")

# --- HEADER & ONBOARDING ---
st.title("🛡️ System Calibration Log")
st.markdown("""
### Objectively tracking recovery metrics.
Progress in nerve-muscle recovery is rarely linear; it looks like a stock market chart. 
This tool uses a **7-day Moving Average** to filter out the 'noise' of a bad day and show you the engineering truth of your healing.
""")

with st.expander("ℹ️ How this app works & Your Privacy"):
    st.write("""
    **Data Sovereignty:** Your recovery data is never stored on this app's servers. It lives exclusively in **your** personal Google Drive.
    **How it Works:** The app reads your public Google Sheet link, performs the statistical math, and renders the charts in your browser. When you close the tab, the connection is severed.
    **Instructions:** 1. Ensure your Google Sheet tab names are 'Calibration Log' and 'Duty Cycle'.
    2. Set your Google Sheet to 'Anyone with the link can view'.
    3. Paste the URL into the sidebar on the left.
    """)

# --- SIDEBAR INPUT ---
st.sidebar.header("Connection Settings")
raw_url = st.sidebar.text_input("Paste Google Sheet URL here:", placeholder="https://docs.google.com/spreadsheets/d/...")

if raw_url:
    try:
        # Clean the URL and extract ID
        clean_url = raw_url.strip()
        if "/d/" in clean_url:
            sheet_id = clean_url.split("/d/")[1].split("/")[0]
            base_query = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
            
            # Pulling Data from Tab 1 & Tab 2
            df_cal = pd.read_csv(f"{base_query}&sheet=Calibration%20Log")
            df_cal['Date'] = pd.to_datetime(df_cal['Date']).dt.date
            
            df_duty = pd.read_csv(f"{base_query}&sheet=Duty%20Cycle")
            df_duty['Date'] = pd.to_datetime(df_duty['Date']).dt.date

            # --- CHART 1: VOLUME TREND ---
            st.subheader("Daily Volume Trend (Wet Weight)")
            daily_vol = df_cal.groupby('Date')['Wet Weight (g)'].sum().reset_index()
            daily_vol['7-Day Avg'] = daily_vol['Wet Weight (g)'].rolling(window=7, min_periods=1).mean()
            
            fig1 = px.bar(daily_vol, x='Date', y='Wet Weight (g)', 
                         labels={'Wet Weight (g)': 'Volume (ml)'},
                         title="Total Daily Leakage (ml)",
                         color_discrete_sequence=['lightgray'])
            fig1.add_scatter(x=daily_vol['Date'], y=daily_vol['7-Day Avg'], name='7-Day Avg', line=dict(color='red', width=3))
            st.plotly_chart(fig1, use_container_width=True)

            # --- CHART 2: PEAK TANK CAPACITY ---
            st.subheader("Operational Capacity (The Tank)")
            daily_max_dry = df_duty.groupby('Date')['Dry Duration (min)'].max().reset_index()
            
            fig2 = px.bar(daily_max_dry, x='Date', y='Dry Duration (min)',
                         labels={'Dry Duration (min)': 'Minutes'},
                         title="Longest Dry Interval Achieved (Minutes)",
                         color_discrete_sequence=['#00CC96'])
            st.plotly_chart(fig2, use_container_width=True)

            # --- CHART 3: ROOT CAUSE ANALYSIS ---
            st.subheader("Failure Mode Analysis")
            triggers = {
                'Pressure [P]': df_cal['Pressure Failure (P)'].sum(),
                'Volume [V]': df_cal['Vol. Failure (V)'].sum(),
                'Fatigue [F]': df_cal['Fatigue Failure (F)'].sum()
            }
            fig3 = px.pie(names=list(triggers.keys()), values=list(triggers.values()), 
                         title="Distribution of Leak Triggers", hole=0.4)
            st.plotly_chart(fig3, use_container_width=True)
            
        else:
            st.error("Please ensure you are pasting a valid Google Sheets URL.")
    except Exception as e:
        st.error(f"Waiting for valid data. Ensure your Sheet is public and tabs are named correctly. Error: {e}")
else:
    st.info("👆 Paste your Google Sheet URL in the sidebar to begin calibration.")
