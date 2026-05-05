"""
Generate synthetic credit card transaction data with anomalies.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Number of transactions
n_transactions = 10000

# Generate timestamps (one per hour over ~416 days)
start_date = datetime(2024, 1, 1)
timestamps = [start_date + timedelta(hours=i) for i in range(n_transactions)]

# Generate normal transaction amounts (gamma distribution = right-skewed, mostly small amounts)
normal_amounts = np.random.gamma(shape=2, scale=50, size=n_transactions)
normal_amounts = np.clip(normal_amounts, 1, 1000)  # Between R1 and R1000

# Introduce anomalies (1% of transactions)
anomaly_count = int(0.01 * n_transactions)
anomaly_indices = np.random.choice(n_transactions, size=anomaly_count, replace=False)

# Anomalies are 5x to 20x larger than normal
amounts = normal_amounts.copy()
amounts[anomaly_indices] = amounts[anomaly_indices] * np.random.uniform(5, 20, size=anomaly_count)

# Create labels
labels = [1 if i in anomaly_indices else 0 for i in range(n_transactions)]

# Create DataFrame
df = pd.DataFrame({
    'timestamp': timestamps,
    'amount': amounts,
    'is_anomaly': labels
})

# Save to CSV
df.to_csv('transactions.csv', index=False)

print(f" Generated {n_transactions} transactions")
print(f"   - Normal: {n_transactions - anomaly_count}")
print(f"   - Anomalies: {anomaly_count}")
print(f"   - File saved: transactions.csv")