import os
import pandas as pd
import streamlit as st

st.title("Sales Dashboard")

@st.cache_data
def load_data(path):
    if path.endswith(".parquet"):
        return pd.read_parquet(path)
    else:
        return pd.read_csv(path)


data_path = os.environ.get("DASHBOARD_DATA", "data/sample_sales.csv")
try:
    df = load_data(data_path)
    st.write(df.head())
    if "revenue" in df.columns:
        st.bar_chart(df.groupby("category")["revenue"].sum())
except Exception as e:
    st.error(f"Failed to load data: {e}")

st.subheader("Prediction")
revenue = st.number_input("Revenue", min_value=0.0, step=0.1)
if st.button("Predict"):
    import requests
    api_url = os.environ.get("API_URL", "http://localhost:8000/predict")
    try:
        resp = requests.post(api_url, json={"revenue": revenue})
        st.write(resp.json())
    except Exception as e:
        st.error(f"API request failed: {e}")

# added new chart placeholder

# added new chart placeholder

# added new chart placeholder 15

# added new chart placeholder 875

# added new chart placeholder 642
