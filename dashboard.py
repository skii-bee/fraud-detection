"""
Streamlit dashboard for fraud detection.
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import anomaly_detector as ad

st.set_page_config(page_title="Fraud Detection Dashboard", layout="wide")

st.title("🔍 Fraud Detection Dashboard")
st.markdown("Detecting anomalous transactions using Rust-powered algorithms")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('transactions.csv')
    return df

df = load_data()

# Sidebar
st.sidebar.header("Detection Settings")
method = st.sidebar.selectbox(
    "Detection Method",
    ["IQR (Rust)", "Z-Score (Rust)"]
)

# Run detection
if st.sidebar.button("Run Detection"):
    amounts = df['amount'].tolist()
    
    with st.spinner("Running Rust anomaly detection..."):
        if method == "IQR (Rust)":
            results = ad.detect_anomalies_iqr(amounts)
        else:
            results = ad.detect_anomalies_zscore(amounts)
    
    df['detected_anomaly'] = results
    
    # Display results
    col1, col2, col3 = st.columns(3)
    
    total = len(df)
    detected = sum(results)
    true_anomalies = sum(df['is_anomaly'] == 1)
    
    col1.metric("Total Transactions", f"{total:,}")
    col2.metric("Detected Anomalies", detected)
    col3.metric("True Anomalies (Ground Truth)", true_anomalies)
    
    # Show anomaly transactions
    st.subheader("🚨 Suspected Anomalies")
    anomalies_df = df[df['detected_anomaly'] == True].head(20)
    st.dataframe(anomalies_df[['timestamp', 'amount']])
    
    # Plot distribution
    st.subheader("Transaction Amount Distribution")
    fig, ax = plt.subplots()
    ax.hist(df['amount'], bins=50, alpha=0.7, label='All')
    ax.hist(anomalies_df['amount'], bins=20, alpha=0.7, label='Anomalies', color='red')
    ax.set_xlabel('Amount (R)')
    ax.set_ylabel('Frequency')
    ax.legend()
    st.pyplot(fig)
    
    # Accuracy
    correct = (df['detected_anomaly'] == df['is_anomaly']).sum()
    accuracy = correct / total * 100
    st.success(f"✅ Accuracy: {accuracy:.2f}%")
else:
    st.info("Select a detection method and click 'Run Detection'")

# Show raw data
with st.expander("View Raw Transaction Data"):
    st.dataframe(df.head(100))
