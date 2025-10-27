import pandas as pd
import streamlit as st
import time
import os

st.set_page_config(page_title="Azerbaijani Website Traffic Monitor", layout="wide")
st.title("🌐 Azerbaijani Website Traffic Dashboard")

csv_path = "website_ai_summaries.csv"

if not os.path.exists(csv_path):
    st.warning("No data yet. Wait for first cycle.")
else:
    df = pd.read_csv(csv_path)
    df = df.sort_values("estimated_visitors", ascending=False).reset_index(drop=True)
    st.dataframe(df)
    st.line_chart(df.set_index("domain")["estimated_visitors"])

# Auto-refresh every minute
time.sleep(60)
st.rerun()
