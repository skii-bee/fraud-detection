"""
Fraud detection using Rust-powered IQR and Z-score methods.
"""
import pandas as pd
import anomaly_detector as ad

# Load data
df = pd.read_csv('transactions.csv')
print(f"Loaded {len(df)} transactions")

# Extract amounts as list
amounts = df['amount'].tolist()

# Run Rust detection methods
print("\n🔍 Running Rust anomaly detection...")
rust_iqr_results = ad.detect_anomalies_iqr(amounts)
rust_zscore_results = ad.detect_anomalies_zscore(amounts)

# Add results to DataFrame
df['rust_iqr_anomaly'] = rust_iqr_results
df['rust_zscore_anomaly'] = rust_zscore_results

# Save the enriched DataFrame
df.to_csv('transactions_with_rust.csv', index=False)

# Compare with ground truth
true_anomalies = df['is_anomaly'] == 1

# Calculate accuracy for IQR
iqr_correct = (df['rust_iqr_anomaly'] == df['is_anomaly']).sum()
iqr_accuracy = iqr_correct / len(df) * 100

zscore_correct = (df['rust_zscore_anomaly'] == df['is_anomaly']).sum()
zscore_accuracy = zscore_correct / len(df) * 100

print(f"\n📊 Results:")
print(f"   IQR Accuracy: {iqr_accuracy:.2f}%")
print(f"   Z-score Accuracy: {zscore_accuracy:.2f}%")

# Show some anomaly examples
print("\n🚨 Detected Anomalies (IQR Method):")
anomalies = df[df['rust_iqr_anomaly'] == True].head(10)
for idx, row in anomalies.iterrows():
    print(f"   Amount: R{row['amount']:.2f} | True Label: {'Anomaly' if row['is_anomaly'] else 'Normal'}")
