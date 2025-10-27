# dashboard.py
import os
import time
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Azerbaijani Website Traffic Dashboard", layout="wide")

st.title("🌐 Azerbaijani Website Traffic Dashboard")
st.subheader("📊 Live visitor estimations (Forex-style updates)")

DATA_PATH = "/website_ai_summaries.csv"

placeholder = st.empty()

def load_data():
    if os.path.exists(DATA_PATH):
        try:
            df = pd.read_csv(DATA_PATH)
            return df
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

while True:
    df = load_data()

    if df.empty:
        placeholder.warning("⏳ Waiting for first results...")
    else:
        expected_cols = ["index", "domain", "summary", "estimated_visitors", "timestamp"]
        available_cols = [c for c in expected_cols if c in df.columns]
        if available_cols:
            with placeholder.container():
                st.dataframe(
                    df[available_cols]
                    .sort_values("index", ascending=True)
                    .reset_index(drop=True),
                    use_container_width=True
                )

                st.bar_chart(df.set_index("domain")["estimated_visitors"], height=300)

                st.caption(f"Last update: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
        else:
            placeholder.info("⚙️ Waiting for complete data fields...")

    time.sleep(10)
    st.rerun()
