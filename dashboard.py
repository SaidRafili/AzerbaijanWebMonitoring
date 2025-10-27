import os
import time
import pandas as pd
import streamlit as st

st.set_page_config(page_title="🌐 Azerbaijani Website Traffic Dashboard", layout="wide")

# Shared CSV path (Render persistent disk)
csv_path = "/data/website_ai_summaries.csv" if os.path.exists("/data") else "website_ai_summaries.csv"

st.title("🌐 Azerbaijani Website Traffic Dashboard")

def run_initial_scrape():
    """Run one quick data collection if file is missing."""
    st.info("Running first data collection... please wait 1–2 minutes.")
    os.system("python forex.py")
    time.sleep(5)

def load_data():
    if not os.path.exists(csv_path):
        run_initial_scrape()
    try:
        return pd.read_csv(csv_path)
    except Exception:
        return pd.DataFrame()

placeholder = st.empty()

# Continuous update loop
while True:
    df = load_data()
    if df.empty:
        placeholder.warning("⏳ No data yet — waiting for first results...")
    else:
        with placeholder.container():
            st.subheader(f"📊 Showing {len(df)} domains")
            st.dataframe(
                df.sort_values("estimated_visitors", ascending=False)
                  .reset_index(drop=True)[["domain", "summary", "estimated_visitors", "timestamp"]]
            )
            st.line_chart(df.set_index("domain")["estimated_visitors"])
    time.sleep(10)
    st.rerun()
