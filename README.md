# 🔍 Fraud Detection – Hybrid Rust + Python

**A production‑ready anomaly detection system that combines high‑performance Rust with Python’s ML ecosystem.**  
Detects fraudulent transactions using IQR, Z‑score, and Isolation Forest – all running locally.

[![Python 3.10](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![Rust](https://img.shields.io/badge/Rust-1.85+-orange.svg)](https://www.rust-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Why This Project?

Most fraud detection demos use only Python. This project goes further:

- **Rust components** for IQR and Z‑score – fast, memory‑safe, and callable from Python via PyO3.
- **Isolation Forest** from scikit‑learn as a benchmark.
- **Complete pipeline** from synthetic data generation to real‑time dashboard.

It demonstrates **cross‑language engineering** – a skill highly valued in low‑latency systems (finance, e‑commerce, cybersecurity).

---

## 🚀 Features

| Feature | Implementation |
|---------|----------------|
| Synthetic transaction data | Python (NumPy / Pandas) |
| IQR anomaly detection | **Rust** (custom implementation) |
| Z‑score anomaly detection | **Rust** (custom implementation) |
| Isolation Forest | scikit‑learn |
| Performance comparison | Accuracy metrics on 10k transactions |
| Interactive dashboard | Streamlit |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Language (core) | Rust 🦀 |
| Language (ML) | Python 🐍 |
| Bridge | PyO3 + Maturin |
| ML library | scikit‑learn |
| Data handling | Pandas, NumPy |
| UI | Streamlit |
| Build system | Cargo + Maturin |

---

## 📊 How It Works

1. **Generate** 10,000 transactions (1% anomalies with unusually large amounts).
2. **Detect anomalies** using three independent methods:
   - **Rust IQR** – flags values outside `[Q1 - 1.5×IQR, Q3 + 1.5×IQR]`.
   - **Rust Z‑score** – flags values beyond ±3 standard deviations.
   - **Isolation Forest** – unsupervised ML model.
3. **Compare** accuracy against ground truth.
4. **Visualise** results in a Streamlit dashboard.

---

## 📁 Repository Structure
fraud-detection/
├── anomaly_detector/ # Rust library (PyO3)
│ ├── Cargo.toml
│ └── src/
│ └── lib.rs
├── generate_data.py # Creates transactions.csv
├── detect_with_rust.py # Calls Rust functions
├── detect_with_sklearn.py # Runs Isolation Forest + comparison
├── dashboard.py # Streamlit UI
├── requirements.txt # Python dependencies
├── README.md
└── .gitignore

---

## 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/skii-bee/fraud-detection.git
cd fraud-detection

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Rust (if not already) – https://rustup.rs/
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Build and install the Rust module
cd anomaly_detector
maturin develop
cd ..

# Generate data
python generate_data.py
🧪 Usage
1. Run Rust detection
bash
python detect_with_rust.py
Outputs accuracy for IQR and Z‑score.

2. Compare with Isolation Forest
bash
python detect_with_sklearn.py
3. Launch interactive dashboard
bash
streamlit run dashboard.py
Visit http://localhost:8501 – upload new data or explore results.

📈 Results (example on 10k transactions)
Method	Accuracy
Rust IQR	97.10%
Rust Z‑score	96.55%
Isolation Forest (sklearn)	99.64%
Note: Isolation Forest uses more complex feature engineering (amount log + hour).

🧠 What I Learned
Writing native Rust functions and exposing them to Python with PyO3.

Implementing statistical anomaly detectors from scratch (IQR, Z‑score).

Building a complete ML pipeline with synthetic data.

Optimising for memory and speed – the Rust module runs in <1ms on 10k transactions.

Debugging cross‑language builds (maturin, Cargo, Python paths).

🚧 Future Improvements
Add time‑window rollings (detect bursts of anomalies)

Implement more advanced algorithms in Rust (Isolation Forest in Rust)

Containerise with Docker

Real‑time transaction stream via WebSockets

📄 License
MIT © Tumelo Tshabalala

🤝 Connect
GitHub
https://github.com/skii-bee
LinkedIn
www.linkedin.com/in/tumelo-tshabalala-988a0228a
Built as part of my journey from mobile‑only coding to production AI engineering.
