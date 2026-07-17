# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is Case 1 for MGMT 59000 (AI for Business Analytics). The goal is to build an interactive Streamlit dashboard for NovaRetail — an omnichannel retailer — that helps a business stakeholder (Sophia Martinez, Director of Customer Intelligence) explore customer revenue, segment risk, and growth opportunities.

The deliverable is `app.py` (Streamlit app) and `requirements.txt`, committed and hosted on GitHub for sharing.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard locally
streamlit run app.py
```

## Data Source

`NR_dataset.xlsx` — single Excel file, one row per transaction. Key fields:

| Field | Notes |
|---|---|
| `CustomerID` | Groups transactions per customer |
| `label` | Segment: Promising, Growth, Stable, Decline |
| `TransactionDate` | Date of purchase |
| `ProductCategory` | Electronics, Clothing, Groceries, Books, Home Appliances |
| `PurchaseAmount` | USD revenue per transaction |
| `CustomerRegion` | Geographic region |
| `RetailChannel` | Online or Physical Store |
| `CustomerSatisfaction` | 1–5 rating |
| `CustomerAgeGroup` | Demographic bucket |
| `CustomerGender` | Demographic field |

Load with `pd.read_excel("NR_dataset.xlsx")`. Aggregate `PurchaseAmount` by `CustomerID` for per-customer revenue.

## Dashboard Requirements

The dashboard must answer three strategic questions:

1. **Which customers generate the most revenue?** — Bar chart: x = CustomerID, y = total PurchaseAmount per customer.
2. **Which segments are at risk?** — Surface customers in the Decline segment; detect early warning signs of reduced engagement.
3. **Where should the company invest?** — Identify growth opportunities across regions, product categories, and sales channels.

All views should support dynamic filtering (sidebar widgets) so Sophia can slice by segment, region, category, channel, etc.

## Architecture

- Single-file app (`app.py`) using Streamlit + Pandas + Plotly (or Altair/Matplotlib).
- Load and cache the Excel file at startup with `@st.cache_data`.
- Sidebar for global filters; main area for KPI metrics, charts, and tables.
- No backend or database — all data lives in the Excel file.
