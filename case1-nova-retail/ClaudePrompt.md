# Prompt to Recreate the NovaRetail Customer Intelligence Dashboard

Use the following prompt to regenerate this dashboard from scratch in a single session.

---

## Prompt

Build a Streamlit customer intelligence dashboard for NovaRetail called `app.py`. Also create a `requirements.txt`. The data source is an Excel file at `case1-nova-retail/NR_dataset.xlsx`.

---

### Data Loading

Load the Excel file with pandas. Apply the following transformations at load time and cache the result with `@st.cache_data`:
- Parse `TransactionDate` as datetime
- Cast `CustomerID` to string
- Create a `Month` column using `df["TransactionDate"].dt.to_period("M").dt.strftime("%b %Y")` (e.g. "Jan 2023", "Feb 2023")
- Drop all rows with any null/NaN values using `dropna()`

After loading, compute `month_order` — the list of unique `Month` values sorted chronologically by parsing them with `pd.to_datetime(m, format="%b %Y")`. This is used to keep time-axis charts in correct order.

---

### Data Dictionary

| Field | Type | Description |
|---|---|---|
| `idx` | int | Sequential index |
| `label` | str | Customer segment: Promising, Growth, Stable, or Decline |
| `CustomerID` | str | Unique customer identifier (treat as a label/name, not a number) |
| `TransactionID` | str | Unique transaction identifier |
| `TransactionDate` | datetime | Date of purchase |
| `ProductCategory` | str | Product category (e.g. Electronics, Clothing, Groceries, Books, Home Appliances) |
| `PurchaseAmount` | float | Transaction value in USD |
| `CustomerAgeGroup` | str | Age range bucket |
| `CustomerGender` | str | Gender |
| `CustomerRegion` | str | Geographic region |
| `CustomerSatisfaction` | int | Rating 1–5 |
| `RetailChannel` | str | "Online" or "Physical Store" |

---

### Page Config

```python
st.set_page_config(page_title="NovaRetail Customer Intelligence", layout="wide")
st.title("NovaRetail Customer Intelligence Dashboard")
```

---

### Sidebar Filters

Place all five filters inside `with st.sidebar`. Use `st.multiselect` for each, defaulting to all options selected. Call `.dropna().unique()` before sorting to avoid TypeError from mixed float/str types. Apply all five filters to produce `filtered_df` used by every chart.

1. **Customer ID** — sorted list of all unique CustomerIDs
2. **Product Category** — sorted list of all unique ProductCategory values
3. **Customer Segment** — sorted list of all unique `label` values
4. **Region** — sorted list of all unique CustomerRegion values
5. **Retail Channel** — sorted list of all unique RetailChannel values

---

### Layout

Use `st.tabs` with four tabs:
1. Revenue by Customer
2. Growth Opportunities
3. Decline & Risk
4. Strategic Recommendations

---

### Tab 1: Revenue by Customer

**Aggregate:** Group `filtered_df` by `["CustomerID", "label"]`, sum `PurchaseAmount` → rename to `TotalRevenue` and `Segment`. Then separately group by `CustomerID` only and sum `TotalRevenue` to get `revenue_totals`, sorted descending.

**Chart 1 — Bar chart** (top):
- `px.bar` using `revenue_totals`
- x = `CustomerID`, y = `TotalRevenue`
- Single color (no category coloring)
- `xaxis_type="category"` to prevent Plotly treating IDs as numeric
- `xaxis_tickangle=-45`
- y-axis: `tickprefix="$"`, `tickformat=",.0f"`
- `height=400`

**Chart 2 — Treemap** (below bar chart):
- `px.treemap` using the `["CustomerID", "label"]` aggregated data
- `path=["Segment", "CustomerID"]` — customers grouped inside segments
- `values="TotalRevenue"`, `color="Segment"`
- `texttemplate="<b>%{label}</b><br>$%{value:,.2f}"`
- `hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.2f}<extra></extra>"`
- `height=550`

**Caption** below treemap: "Top 5 customers by revenue: ID XXXXX ($X,XXX.XX), ..."

---

### Tab 2: Growth Opportunities

**Chart 1 — Stacked area chart** (full width):
- Group `filtered_df` by `["Month", "label"]`, sum `PurchaseAmount` → `TotalRevenue`, rename `label` → `Segment`
- `px.area`, x=`Month`, y=`TotalRevenue`, color=`Segment`
- Pass `category_orders={"Month": month_order}` to ensure Jan appears left of Feb
- y-axis: dollar prefix and comma format
- Legend horizontal, below chart

**Charts 2 & 3** — side by side using `st.columns(2)`:

**Left — Heatmap:**
- Group `filtered_df` by `["CustomerRegion", "ProductCategory"]`, sum `PurchaseAmount`
- Pivot: index=`CustomerRegion`, columns=`ProductCategory`, values=`PurchaseAmount`, fill NaN with 0
- `px.imshow` with `color_continuous_scale="Blues"`, `aspect="auto"`
- Title: "Revenue Heatmap: Region × Product Category"
- `height=420`

**Right — Scatter plot:**
- Group `filtered_df` by `["CustomerID", "label"]`, aggregate: `TransactionCount` = count of TransactionID, `AvgPurchaseAmount` = mean of PurchaseAmount, `TotalRevenue` = sum of PurchaseAmount
- `px.scatter`, x=`TransactionCount`, y=`AvgPurchaseAmount`, color=`Segment`, size=`TotalRevenue`
- Include `CustomerID` and `TotalRevenue` in hover_data
- y-axis: dollar format
- `height=420`, legend horizontal below

---

### Tab 3: Decline & Risk

**Chart 1 — Line chart** (full width):
- Group `filtered_df` by `["Month", "label"]`, count unique CustomerIDs → `CustomerCount`, rename `label` → `Segment`
- `px.line`, x=`Month`, y=`CustomerCount`, color=`Segment`, `markers=True`
- Pass `category_orders={"Month": month_order}`
- Title: "Active Customers per Segment Over Time"
- Legend horizontal, below chart

**Charts 2 & 3** — side by side using `st.columns(2)`:

**Left — Box plot:**
- `px.box` on `filtered_df`, x=`label` (renamed to `Segment`), y=`CustomerSatisfaction`, color=`Segment`
- `showlegend=False`, `height=400`
- Title: "Satisfaction Distribution by Segment"

**Right — Data table:**
- Filter `filtered_df` to `label == "Decline"`
- If empty, show `st.info("No Decline segment customers match the current filters.")`
- Otherwise group by `CustomerID`, aggregate: `TotalRevenue` (sum PurchaseAmount), `Transactions` (count TransactionID), `LastTransaction` (max TransactionDate), `AvgSatisfaction` (mean CustomerSatisfaction)
- Sort by `TotalRevenue` descending
- Format: `LastTransaction` → `strftime("%Y-%m-%d")`, `TotalRevenue` → `"${:,.2f}"`, `AvgSatisfaction` → `.round(1)`
- Display with `st.dataframe(..., hide_index=True, height=380)`

---

### Tab 4: Strategic Recommendations

**Row 1** — `st.columns(2)`:

**Left — Grouped bar chart:**
- Group `filtered_df` by `["RetailChannel", "label"]`, sum `PurchaseAmount` → `TotalRevenue`, rename `label` → `Segment`
- `px.bar`, x=`RetailChannel`, y=`TotalRevenue`, color=`Segment`, `barmode="group"`
- y-axis: dollar format, `height=400`, legend horizontal below
- Title: "Revenue by Retail Channel & Segment"

**Right — Horizontal bar chart:**
- Group `filtered_df` by `ProductCategory`, mean `CustomerSatisfaction` → `AvgSatisfaction`, sort ascending
- `px.bar`, x=`AvgSatisfaction`, y=`ProductCategory`, `orientation="h"`
- `color="AvgSatisfaction"`, `color_continuous_scale="RdYlGn"`, `coloraxis_showscale=False`
- `xaxis_range=[0, 5]`, `height=400`
- Title: "Avg Customer Satisfaction by Product Category"

**Row 2** — `st.subheader("Revenue by Demographics & Segment")`, then `st.columns(2)`:

**Left — Stacked bar by age group:**
- Group `filtered_df` by `["CustomerAgeGroup", "label"]`, sum `PurchaseAmount` → `TotalRevenue`, rename `label` → `Segment`
- `px.bar`, x=`CustomerAgeGroup`, y=`TotalRevenue`, color=`Segment`, `barmode="stack"`
- y-axis: dollar format, `height=380`, legend horizontal below
- Title: "Revenue by Age Group & Segment"

**Right — Donut chart:**
- Group `filtered_df` by `CustomerGender`, sum `PurchaseAmount` → `TotalRevenue`
- `px.pie`, `names="CustomerGender"`, `values="TotalRevenue"`, `hole=0.4`
- `height=380`
- Title: "Revenue Share by Gender"

---

### requirements.txt

```
streamlit>=1.35.0
pandas>=2.0.0
plotly>=5.20.0
openpyxl>=3.1.0
```

### Run command

```bash
streamlit run app.py
```
