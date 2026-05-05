"""
Fraud detection using scikit-learn Isolation Forest.
Compares with Rust IQR and Z-score columns (must be generated first by detect_with_rust.py).
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

# Load data – try enriched version first
import os
if os.path.exists('transactions_with_rust.csv'):
    df = pd.read_csv('transactions_with_rust.csv')
    print("Loaded enriched data with Rust detection columns")
else:
    df = pd.read_csv('transactions.csv')
    print("Loaded original data (run detect_with_rust.py first for full comparison)")

print(f"Loaded {len(df)} transactions")

# ---- sklearn Isolation Forest ----
df['amount_log'] = np.log1p(df['amount'])
df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
features = ['amount', 'amount_log', 'hour']
model = IsolationForest(contamination=0.01, random_state=42)
model.fit(df[features].values)
df['sklearn_anomaly'] = model.predict(df[features].values) == -1

# Calculate accuracy
true = df['is_anomaly']
sklearn_correct = (df['sklearn_anomaly'] == true).sum()
sklearn_accuracy = sklearn_correct / len(df) * 100

print(f"\n📊 Isolation Forest Accuracy: {sklearn_accuracy:.2f}%")

# ---- Compare with Rust methods (if columns exist) ----
print("\n📈 Method Comparison:")

if 'rust_iqr_anomaly' in df.columns:
    iqr_correct = (df['rust_iqr_anomaly'] == true).sum()
    iqr_acc = iqr_correct / len(df) * 100
    print(f"   Rust IQR: {iqr_acc:.2f}%")
else:
    print("   Rust IQR: not found (run detect_with_rust.py first)")

if 'rust_zscore_anomaly' in df.columns:
    zscore_correct = (df['rust_zscore_anomaly'] == true).sum()
    zscore_acc = zscore_correct / len(df) * 100
    print(f"   Rust Z-score: {zscore_acc:.2f}%")
else:
    print("   Rust Z-score: not found (run detect_with_rust.py first)")

print(f"   sklearn Isolation Forest: {sklearn_accuracy:.2f}%")