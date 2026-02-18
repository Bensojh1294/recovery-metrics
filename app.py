import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="System Calibration Dashboard", layout="wide")

st.title("🛡️ System Calibration Log")
st.write("Objectively tracking postoperative  metrics.")

sheet_url = st.sidebar.text_input("Paste Google Sheet URL here:", 
                                 placeholder="https://docs.google.com/spreadsheets/d/...")

if sheet_url:
    try:
        csv_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=').replace('/edit', '/export?format=csv')
        df = pd.read_csv(csv_url)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')

        # --- MATH: MOVING AVERAGE & PROJECTION ---
        df['7-Day Avg'] = df['Wet Weight (g)'].rolling(window=7).mean()
        
        # Linear Regression for Projection (Last 14 days)
        recent_data = df.dropna(subset=['7-Day Avg']).tail(14)
        if len(recent_data) > 3:
            y = recent_data['7-Day Avg'].values
            x = np.arange(len(y)).reshape(-1, 1)
            # Simple slope calculation
            slope, intercept = np.polyfit(x.flatten(), y, 1)
            
            if slope < 0:
                days_to_zero = -intercept / slope
                projected_date = recent_data['Date'].max() + timedelta(days=int(days_to_zero))
                st.success(f"📈 **Engineering Forecast:** Based on your current 7-day trend, your projected 'Zero Leak' date is approximately **{projected_date.strftime('%B %d, %Y')}**.")
            else:
                st.warning("📈 **Trend Note:** Volume is currently stable. Keep tracking to establish a downward slope.")

        # --- CHARTS ---
        st.subheader("Volume Trend (Lower is Better)")
        fig1 = px.line(df, x='Date', y=['Wet Weight (g)', '7-Day Avg'],
                      labels={'value': 'Milliliters (ml)', 'variable': 'Metric'},
                      color_discrete_map={'Wet Weight (g)': 'lightgray', '7-Day Avg': 'red'})
        st.plotly_chart(fig1, use_container_width=True)

    except Exception as e:
        st.error(f"Waiting for valid data... Error: {e}")
else:
    st.info("👆 Paste your Google Sheet URL in the sidebar to begin.")
