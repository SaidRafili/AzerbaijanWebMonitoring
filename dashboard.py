import pandas as pd
import streamlit as st
import time
import os

st.set_page_config(page_title="🌐 Azerbaijani Website Traffic Ticker", layout="wide")

csv_path = "/data/website_ai_summaries.csv" if os.path.exists("/data") else "website_ai_summaries.csv"
MAX_DISPLAY = 100

st.title("🌐 Azerbaijani Website Traffic Dashboard")
placeholder = st.empty()

def load_data():
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    try:
        df = pd.read_csv(csv_path)
        return df.tail(MAX_DISPLAY)
    except Exception:
        return pd.DataFrame()

# Live ticker
while True:
    df = load_data()
    if df.empty:
        placeholder.warning("⏳ No data yet — waiting for first results...")
    else:
        with placeholder.container():
            st.subheader(f"📊 Latest {len(df)} Domains")
            st.dataframe(df[["domain", "summary", "estimated_visitors", "timestamp"]].sort_values("timestamp", ascending=False))
            st.line_chart(df.set_index("domain")["estimated_visitors"])
# Auto-refresh every minute
time.sleep(5)
st.rerun()

