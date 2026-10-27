# Choice Logistics - Operational Performance PoC

**Author:** Carlos Silveira
**Objective:** Proof of Concept (PoC) for the Business Analyst role (EMEA & APAC Operations).

## 🎯 The Problem
Choice Logistics currently measures its 4PL operations through a mix of manual exports and spreadsheets. There is no centralized performance framework to track SLA breaches, carrier bottlenecks, and cost-to-serve in real-time.

## 🛠️ The Solution
This PoC demonstrates how to build an end-to-end performance measurement pipeline:
1. **Data Generation:** Simulates 1,000 orders across EMEA/APAC, including intentional bottlenecks (e.g., specific carriers failing on Fridays).
2. **KPI Processing (Python/Pandas):** Calculates Order Cycle Time, SLA Attainment, Exception Rate, and Cost-to-Serve.
3. **Interactive Dashboard (Streamlit/Plotly):** Provides a clean, executive-level UI with dynamic filters (Region, Carrier, Client) to drill down into operational pain points.

## 🚀 How to Run Locally
```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/cfasilveira/proj_choice.git
cd proj_choice

# Create virtual environment and install dependencies
uv venv --python 3.14
uv add pandas streamlit plotly

# Generate simulated data
uv run python gerar_dados.py

# Run the dashboard
uv run streamlit run dashboard.py