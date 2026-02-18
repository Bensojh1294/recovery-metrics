import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="System Calibration Dashboard", layout="wide")

st.title("🛡️ System Calibration Log")
st.write("Objectively tracking recovery metrics based on your engineered protocol.")

# Sidebar for the Link
raw_url = st.sidebar.text_input("Paste Google Sheet URL here:")

if raw_url:
    try:
        # Clean the URL of any accidental spaces or control characters
        clean_url = raw_url.strip()
        
        # Extract the base ID of the spreadsheet
        if "/d/" in clean_url:
            sheet_id = clean_url.split("/d/")[1].split("/")[0]
            base_query = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
            
            # Pulling Tab 1: Calibration Log
            cal_url = f"{base_query}&sheet=Calibration%20Log"
            df_cal = pd.read_csv(cal_url)
            df_cal['Date'] = pd.to_datetime(df_cal['Date'])
            
            # Pulling Tab 2: Duty Cycle
            duty_url = f"{base_query}&sheet=Duty%20Cycle"
            df_duty = pd.read_csv(duty_url)
            df_duty['Date'] = pd.to_datetime(df_duty['Date'])

            # --- CHART 1: VOLUME TREND ---
            st.subheader("Volume Trend (Wet Weight)")
            df_cal = df_cal.sort_values('Date')
            df_cal['7-Day Avg'] = df_cal['Wet Weight (g)'].rolling(window=7).mean()
            
            fig1 = px.line(df_cal, x='Date', y=['Wet Weight (g)', '7-Day Avg'],
                          labels={'value': 'Milliliters (ml)', 'variable': 'Metric'},
                          color_discrete_map={'Wet Weight (g)': 'lightgray', '7-Day Avg': 'red'})
            st.plotly_chart(fig1, use_container_width=True)

            # --- CHART 2: TANK CAPACITY ---
            st.subheader("Operational Capacity (The Tank)")
            fig2 = px.bar(df_duty, x='Date', y='Dry Duration (min)',
                         color_discrete_sequence=['#00CC96'])
            st.plotly_chart(fig2, use_container_width=True)

            # --- CHART 3: ROOT CAUSE ANALYSIS ---
            st.subheader("Failure Mode Analysis")
            triggers = {
                'Pressure [P]': df_cal['Pressure Failure (P)'].sum(),
                'Volume [V]': df_cal['Vol. Failure (V)'].sum(),
                'Fatigue [F]': df_cal['Fatigue Failure (F)'].sum()
            }
            fig3 = px.pie(names=list(triggers.keys()), values=list(triggers.values()), hole=0.4)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.error("Please ensure you are pasting a valid Google Sheets URL.")

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("👆 Paste your Google Sheet URL in the sidebar to begin.")
