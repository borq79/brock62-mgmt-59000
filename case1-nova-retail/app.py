import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NovaRetail Customer Intelligence", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel("case1-nova-retail/NR_dataset.xlsx")
    df["TransactionDate"] = pd.to_datetime(df["TransactionDate"])
    df["CustomerID"] = df["CustomerID"].astype(str)
    df["Month"] = df["TransactionDate"].dt.to_period("M").dt.strftime("%b %Y")
    df = df.dropna()
    return df

df = load_data()

month_order = sorted(df["Month"].unique(), key=lambda m: pd.to_datetime(m, format="%b %Y"))

# ── Sidebar filters ──────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Filters")

    all_customers = sorted(df["CustomerID"].dropna().unique().tolist())
    selected_customers = st.multiselect("Customer ID", options=all_customers, default=all_customers)

    all_categories = sorted(df["ProductCategory"].dropna().unique().tolist())
    selected_categories = st.multiselect("Product Category", options=all_categories, default=all_categories)

    all_segments = sorted(df["label"].dropna().unique().tolist())
    selected_segments = st.multiselect("Customer Segment", options=all_segments, default=all_segments)

    all_regions = sorted(df["CustomerRegion"].dropna().unique().tolist())
    selected_regions = st.multiselect("Region", options=all_regions, default=all_regions)

    all_channels = sorted(df["RetailChannel"].dropna().unique().tolist())
    selected_channels = st.multiselect("Retail Channel", options=all_channels, default=all_channels)

filtered_df = df[
    df["CustomerID"].isin(selected_customers) &
    df["ProductCategory"].isin(selected_categories) &
    df["label"].isin(selected_segments) &
    df["CustomerRegion"].isin(selected_regions) &
    df["RetailChannel"].isin(selected_channels)
]

# ── Dashboard ────────────────────────────────────────────────────────────────

st.title("NovaRetail Customer Intelligence Dashboard")

tab1, tab2, tab3, tab4 = st.tabs([
    "Revenue by Customer",
    "Growth Opportunities",
    "Decline & Risk",
    "Strategic Recommendations",
])

# ── Tab 1: Revenue by Customer ───────────────────────────────────────────────

with tab1:
    st.header("Revenue by Customer")

    revenue_by_customer = (
        filtered_df.groupby(["CustomerID", "label"])["PurchaseAmount"]
        .sum()
        .reset_index()
        .rename(columns={"PurchaseAmount": "TotalRevenue", "label": "Segment"})
    )

    revenue_totals = (
        revenue_by_customer.groupby("CustomerID")["TotalRevenue"]
        .sum()
        .reset_index()
        .sort_values("TotalRevenue", ascending=False)
    )

    fig_bar = px.bar(
        revenue_totals,
        x="CustomerID",
        y="TotalRevenue",
        labels={"CustomerID": "Customer ID", "TotalRevenue": "Total Revenue (USD)"},
        title="Total Revenue by Customer (sorted by highest revenue)",
    )
    fig_bar.update_layout(
        xaxis_tickangle=-45,
        xaxis_type="category",
        yaxis_tickprefix="$",
        yaxis_tickformat=",.0f",
        height=400,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    fig = px.treemap(
        revenue_by_customer,
        path=["Segment", "CustomerID"],
        values="TotalRevenue",
        color="Segment",
        hover_data={"TotalRevenue": ":.2f"},
        labels={"TotalRevenue": "Total Revenue (USD)", "Segment": "Segment", "CustomerID": "Customer ID"},
        title="Total Revenue by Customer (sized by revenue, colored by segment)",
    )
    fig.update_traces(
        texttemplate="<b>%{label}</b><br>$%{value:,.2f}",
        hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.2f}<extra></extra>",
    )
    fig.update_layout(height=550)
    st.plotly_chart(fig, use_container_width=True)

    top_customers = revenue_by_customer.sort_values("TotalRevenue", ascending=False).head(5)
    st.caption(
        "Top 5 customers by revenue: "
        + ", ".join(f"ID {row.CustomerID} (${row.TotalRevenue:,.2f})" for row in top_customers.itertuples())
    )

# ── Tab 2: Growth Opportunities ──────────────────────────────────────────────

with tab2:
    st.header("Growth Opportunities")

    # Stacked area: monthly revenue by segment
    st.subheader("Revenue Trend by Customer Segment")
    trend_df = (
        filtered_df.groupby(["Month", "label"])["PurchaseAmount"]
        .sum()
        .reset_index()
        .rename(columns={"PurchaseAmount": "TotalRevenue", "label": "Segment"})
    )
    fig_area = px.area(
        trend_df,
        x="Month",
        y="TotalRevenue",
        color="Segment",
        category_orders={"Month": month_order},
        labels={"Month": "Month", "TotalRevenue": "Total Revenue (USD)", "Segment": "Segment"},
        title="Monthly Revenue by Customer Segment",
    )
    fig_area.update_layout(
        yaxis_tickprefix="$",
        yaxis_tickformat=",.0f",
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig_area, use_container_width=True)

    col1, col2 = st.columns(2)

    # Heatmap: Region × ProductCategory
    with col1:
        st.subheader("Revenue by Region & Category")
        heatmap_df = (
            filtered_df.groupby(["CustomerRegion", "ProductCategory"])["PurchaseAmount"]
            .sum()
            .reset_index()
            .pivot(index="CustomerRegion", columns="ProductCategory", values="PurchaseAmount")
            .fillna(0)
        )
        fig_heat = px.imshow(
            heatmap_df,
            labels=dict(x="Product Category", y="Region", color="Revenue (USD)"),
            title="Revenue Heatmap: Region × Product Category",
            color_continuous_scale="Blues",
            aspect="auto",
        )
        fig_heat.update_layout(height=420)
        st.plotly_chart(fig_heat, use_container_width=True)

    # Scatter: transaction frequency vs avg purchase amount per customer
    with col2:
        st.subheader("Customer Purchase Behavior")
        scatter_df = (
            filtered_df.groupby(["CustomerID", "label"])
            .agg(
                TransactionCount=("TransactionID", "count"),
                AvgPurchaseAmount=("PurchaseAmount", "mean"),
                TotalRevenue=("PurchaseAmount", "sum"),
            )
            .reset_index()
            .rename(columns={"label": "Segment"})
        )
        fig_scatter = px.scatter(
            scatter_df,
            x="TransactionCount",
            y="AvgPurchaseAmount",
            color="Segment",
            size="TotalRevenue",
            hover_data={"CustomerID": True, "TotalRevenue": ":.2f"},
            labels={
                "TransactionCount": "Number of Transactions",
                "AvgPurchaseAmount": "Avg Purchase Amount (USD)",
                "Segment": "Segment",
            },
            title="Purchase Frequency vs. Avg Spend per Customer",
        )
        fig_scatter.update_layout(
            yaxis_tickprefix="$",
            yaxis_tickformat=",.0f",
            height=420,
            legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

# ── Tab 3: Decline & Risk ────────────────────────────────────────────────────

with tab3:
    st.header("Early Warning Signs of Decline")

    # Line chart: unique customers per segment per month
    st.subheader("Active Customers per Segment Over Time")
    segment_count_df = (
        filtered_df.groupby(["Month", "label"])["CustomerID"]
        .nunique()
        .reset_index()
        .rename(columns={"CustomerID": "CustomerCount", "label": "Segment"})
    )
    fig_line = px.line(
        segment_count_df,
        x="Month",
        y="CustomerCount",
        color="Segment",
        markers=True,
        category_orders={"Month": month_order},
        labels={"Month": "Month", "CustomerCount": "Unique Customers", "Segment": "Segment"},
        title="Active Customers per Segment Over Time",
    )
    fig_line.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig_line, use_container_width=True)

    col1, col2 = st.columns(2)

    # Box plot: satisfaction by segment
    with col1:
        st.subheader("Customer Satisfaction by Segment")
        fig_box = px.box(
            filtered_df.rename(columns={"label": "Segment"}),
            x="Segment",
            y="CustomerSatisfaction",
            color="Segment",
            labels={"CustomerSatisfaction": "Satisfaction Score (1–5)", "Segment": "Segment"},
            title="Satisfaction Distribution by Segment",
        )
        fig_box.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_box, use_container_width=True)

    # Table: Decline customers detail
    with col2:
        st.subheader("Decline Segment — Customer Detail")
        decline_df = filtered_df[filtered_df["label"] == "Decline"]
        if decline_df.empty:
            st.info("No Decline segment customers match the current filters.")
        else:
            decline_summary = (
                decline_df.groupby("CustomerID")
                .agg(
                    TotalRevenue=("PurchaseAmount", "sum"),
                    Transactions=("TransactionID", "count"),
                    LastTransaction=("TransactionDate", "max"),
                    AvgSatisfaction=("CustomerSatisfaction", "mean"),
                )
                .reset_index()
                .sort_values("TotalRevenue", ascending=False)
            )
            decline_summary["LastTransaction"] = decline_summary["LastTransaction"].dt.strftime("%Y-%m-%d")
            decline_summary["TotalRevenue"] = decline_summary["TotalRevenue"].map("${:,.2f}".format)
            decline_summary["AvgSatisfaction"] = decline_summary["AvgSatisfaction"].round(1)
            st.dataframe(decline_summary, use_container_width=True, hide_index=True, height=380)

# ── Tab 4: Strategic Recommendations ────────────────────────────────────────

with tab4:
    st.header("Strategic Recommendations")

    col1, col2 = st.columns(2)

    # Grouped bar: revenue by channel and segment
    with col1:
        st.subheader("Revenue by Channel & Segment")
        channel_seg_df = (
            filtered_df.groupby(["RetailChannel", "label"])["PurchaseAmount"]
            .sum()
            .reset_index()
            .rename(columns={"PurchaseAmount": "TotalRevenue", "label": "Segment"})
        )
        fig_channel = px.bar(
            channel_seg_df,
            x="RetailChannel",
            y="TotalRevenue",
            color="Segment",
            barmode="group",
            labels={"RetailChannel": "Retail Channel", "TotalRevenue": "Total Revenue (USD)", "Segment": "Segment"},
            title="Revenue by Retail Channel & Segment",
        )
        fig_channel.update_layout(
            yaxis_tickprefix="$",
            yaxis_tickformat=",.0f",
            height=400,
            legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_channel, use_container_width=True)

    # Horizontal bar: avg satisfaction by product category
    with col2:
        st.subheader("Avg Satisfaction by Product Category")
        sat_cat_df = (
            filtered_df.groupby("ProductCategory")["CustomerSatisfaction"]
            .mean()
            .reset_index()
            .rename(columns={"CustomerSatisfaction": "AvgSatisfaction"})
            .sort_values("AvgSatisfaction")
        )
        fig_sat = px.bar(
            sat_cat_df,
            x="AvgSatisfaction",
            y="ProductCategory",
            orientation="h",
            color="AvgSatisfaction",
            color_continuous_scale="RdYlGn",
            labels={"AvgSatisfaction": "Avg Satisfaction (1–5)", "ProductCategory": "Product Category"},
            title="Avg Customer Satisfaction by Product Category",
        )
        fig_sat.update_layout(
            coloraxis_showscale=False,
            height=400,
            xaxis_range=[0, 5],
        )
        st.plotly_chart(fig_sat, use_container_width=True)

    # Demographics
    st.subheader("Revenue by Demographics & Segment")
    col3, col4 = st.columns(2)

    with col3:
        age_seg_df = (
            filtered_df.groupby(["CustomerAgeGroup", "label"])["PurchaseAmount"]
            .sum()
            .reset_index()
            .rename(columns={"PurchaseAmount": "TotalRevenue", "label": "Segment"})
        )
        fig_age = px.bar(
            age_seg_df,
            x="CustomerAgeGroup",
            y="TotalRevenue",
            color="Segment",
            barmode="stack",
            labels={"CustomerAgeGroup": "Age Group", "TotalRevenue": "Total Revenue (USD)", "Segment": "Segment"},
            title="Revenue by Age Group & Segment",
        )
        fig_age.update_layout(
            yaxis_tickprefix="$",
            yaxis_tickformat=",.0f",
            height=380,
            legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_age, use_container_width=True)

    with col4:
        gender_df = (
            filtered_df.groupby("CustomerGender")["PurchaseAmount"]
            .sum()
            .reset_index()
            .rename(columns={"PurchaseAmount": "TotalRevenue"})
        )
        fig_gender = px.pie(
            gender_df,
            names="CustomerGender",
            values="TotalRevenue",
            title="Revenue Share by Gender",
            hole=0.4,
        )
        fig_gender.update_layout(height=380)
        st.plotly_chart(fig_gender, use_container_width=True)
