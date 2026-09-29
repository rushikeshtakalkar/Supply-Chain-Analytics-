import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Supply Chain & Inventory Analytics",
    page_icon="📦",
    layout="wide",
)

st.title("📦 Supply Chain & Inventory Optimization Analytics")
st.caption("Portfolio demo • Excel + SQL + Power BI concepts • Synthetic dataset")

DATA_FILE = Path(__file__).with_name("Supply_Chain_Inventory_Analytics.xlsx")

@st.cache_data
def load_data(file):
    orders = pd.read_excel(file, sheet_name="Order_Fact")
    inventory = pd.read_excel(file, sheet_name="Inventory_Snapshot")
    suppliers = pd.read_excel(file, sheet_name="Supplier_Scorecard")
    orders["Order_Date"] = pd.to_datetime(orders["Order_Date"], errors="coerce")
    return orders, inventory, suppliers

uploaded = st.sidebar.file_uploader(
    "Upload project Excel workbook",
    type=["xlsx"],
    help="Upload Supply_Chain_Inventory_Analytics.xlsx if it is not beside app.py."
)

source = uploaded if uploaded is not None else (str(DATA_FILE) if DATA_FILE.exists() else None)

if source is None:
    st.warning(
        "Excel workbook not found. Put Supply_Chain_Inventory_Analytics.xlsx in the same "
        "folder as app.py, or upload it using the sidebar."
    )
    st.stop()

try:
    orders, inventory, suppliers = load_data(source)
except Exception as exc:
    st.error(f"Could not read the workbook: {exc}")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")
min_date = orders["Order_Date"].min().date()
max_date = orders["Order_Date"].max().date()
date_range = st.sidebar.date_input(
    "Order date range", value=(min_date, max_date),
    min_value=min_date, max_value=max_date
)

regions = sorted(orders["Region"].dropna().unique().tolist())
warehouses = sorted(orders["Warehouse"].dropna().unique().tolist())
categories = sorted(orders["Category"].dropna().unique().tolist())
channels = sorted(orders["Sales_Channel"].dropna().unique().tolist())

selected_regions = st.sidebar.multiselect("Region", regions, default=regions)
selected_warehouses = st.sidebar.multiselect("Warehouse", warehouses, default=warehouses)
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)
selected_channels = st.sidebar.multiselect("Sales channel", channels, default=channels)

filtered = orders[
    orders["Region"].isin(selected_regions)
    & orders["Warehouse"].isin(selected_warehouses)
    & orders["Category"].isin(selected_categories)
    & orders["Sales_Channel"].isin(selected_channels)
].copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    filtered = filtered[
        filtered["Order_Date"].dt.date.between(date_range[0], date_range[1])
    ]

if filtered.empty:
    st.info("No records match these filters. Change the selections in the sidebar.")
    st.stop()

# Metrics
order_count = filtered["Order_ID"].nunique()
units_ordered = filtered["Order_Qty"].sum()
units_delivered = filtered["Delivered_Qty"].sum()
revenue = (filtered["Delivered_Qty"] * filtered["Unit_Price_INR"]).sum()
cogs = (filtered["Delivered_Qty"] * filtered["Unit_Cost_INR"]).sum()
gross_profit = revenue - cogs
on_time_complete = (
    (filtered["Actual_Lead_Days"] <= filtered["Promised_Days"])
    & (filtered["Delivered_Qty"] == filtered["Order_Qty"])
).mean()
late_count = (filtered["Actual_Lead_Days"] > filtered["Promised_Days"]).sum()
fill_rate = units_delivered / units_ordered if units_ordered else 0

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Order lines", f"{order_count:,}")
m2.metric("Units delivered", f"{units_delivered:,.0f}")
m3.metric("Revenue", f"₹{revenue:,.0f}")
m4.metric("Gross profit", f"₹{gross_profit:,.0f}")
m5.metric("On-time & complete", f"{on_time_complete:.1%}")

m6, m7, m8 = st.columns(3)
m6.metric("Fill rate", f"{fill_rate:.1%}")
m7.metric("Late order lines", f"{late_count:,}")
m8.metric("Gross margin", f"{gross_profit / revenue:.1%}" if revenue else "0.0%")

tab1, tab2, tab3, tab4 = st.tabs([
    "Executive Overview", "Inventory Optimization",
    "Delivery Performance", "Data Explorer"
])

with tab1:
    left, right = st.columns(2)
    monthly = filtered.assign(
        Month=filtered["Order_Date"].dt.to_period("M").astype(str),
        Revenue=filtered["Delivered_Qty"] * filtered["Unit_Price_INR"],
        Gross_Profit=filtered["Delivered_Qty"] *
            (filtered["Unit_Price_INR"] - filtered["Unit_Cost_INR"])
    ).groupby("Month", as_index=False)[["Revenue", "Gross_Profit"]].sum()
    with left:
        st.subheader("Monthly revenue")
        fig = px.line(monthly, x="Month", y="Revenue", markers=True,
                      title="Revenue by month")
        fig.update_layout(xaxis_title="", yaxis_title="Revenue (INR)")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Revenue by category")
        cat = filtered.assign(
            Revenue=filtered["Delivered_Qty"] * filtered["Unit_Price_INR"],
            Gross_Profit=filtered["Delivered_Qty"] *
                (filtered["Unit_Price_INR"] - filtered["Unit_Cost_INR"])
        ).groupby("Category", as_index=False)[["Revenue", "Gross_Profit"]].sum()
        fig = px.bar(cat, x="Category", y=["Revenue", "Gross_Profit"],
                     barmode="group", title="Revenue and gross profit")
        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.subheader("Order status")
        status = filtered["Order_Status"].value_counts().rename_axis("Order Status").reset_index(name="Orders")
        fig = px.pie(status, names="Order Status", values="Orders", hole=0.45)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Revenue by sales channel")
        channel = filtered.assign(
            Revenue=filtered["Delivered_Qty"] * filtered["Unit_Price_INR"]
        ).groupby("Sales_Channel", as_index=False)["Revenue"].sum()
        fig = px.bar(channel, x="Sales_Channel", y="Revenue", title="Revenue by channel")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Inventory and replenishment")
    inv = inventory.copy()
    inv["Inventory_Position"] = inv["On_Hand_Units"] + inv["On_Order_Units"]
    inv["Reorder_Gap"] = inv["Reorder_Point_Units"] - inv["Inventory_Position"]
    attention = inv[inv["Stock_Status"] != "Healthy"]
    a, b, c = st.columns(3)
    a.metric("Inventory value", f"₹{inv['Inventory_Value_INR'].sum():,.0f}")
    b.metric("SKUs needing attention", f"{len(attention)}")
    c.metric("Reorder now", f"{(inv['Stock_Status'] == 'Reorder Now').sum()}")

    st.subheader("On-hand stock vs reorder point")
    fig = px.bar(inv.sort_values("Reorder_Gap", ascending=False),
                 x="Product", y=["On_Hand_Units", "Reorder_Point_Units"],
                 barmode="group", title="Stock position by product")
    fig.update_layout(xaxis_title="", yaxis_title="Units")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("SKU replenishment table")
    display_inv = inv[[
        "SKU", "Product", "Warehouse", "On_Hand_Units", "On_Order_Units",
        "Safety_Stock_Units", "Reorder_Point_Units", "Inventory_Position",
        "Inventory_Value_INR", "Stock_Status"
    ]].sort_values(["Stock_Status", "Reorder_Gap"], ascending=[True, False])
    st.dataframe(display_inv, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Delivery and supplier performance")
    delivery = filtered.copy()
    delivery["Late_Flag"] = delivery["Actual_Lead_Days"] > delivery["Promised_Days"]
    warehouse_perf = delivery.groupby("Warehouse", as_index=False).agg(
        Order_Lines=("Order_ID", "count"),
        Late_Orders=("Late_Flag", "sum"),
        Avg_Lead_Days=("Actual_Lead_Days", "mean")
    )
    warehouse_perf["Late_Delivery_Pct"] = 100 * warehouse_perf["Late_Orders"] / warehouse_perf["Order_Lines"]
    left, right = st.columns(2)
    with left:
        fig = px.bar(warehouse_perf.sort_values("Late_Delivery_Pct", ascending=False),
                     x="Warehouse", y="Late_Delivery_Pct",
                     title="Late delivery rate by warehouse", text_auto=".1f")
        fig.update_layout(yaxis_title="Late orders (%)")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        monthly_delay = delivery.assign(
            Month=delivery["Order_Date"].dt.to_period("M").astype(str),
            Late=delivery["Actual_Lead_Days"] > delivery["Promised_Days"]
        ).groupby("Month", as_index=False).agg(Late_Rate=("Late", "mean"))
        monthly_delay["Late_Rate"] *= 100
        fig = px.line(monthly_delay, x="Month", y="Late_Rate", markers=True,
                      title="Monthly late delivery rate")
        fig.update_layout(yaxis_title="Late orders (%)", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Supplier scorecard")
    st.dataframe(
        suppliers.sort_values("On_Time_Delivery_Pct"),
        use_container_width=True, hide_index=True
    )

with tab4:
    st.subheader("Filtered order records")
    st.caption("Use the sidebar filters to narrow the data. Download the filtered rows for further analysis.")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered orders as CSV", csv,
                       file_name="filtered_supply_chain_orders.csv",
                       mime="text/csv")

st.divider()
st.caption(
    "Data disclosure: this is a synthetic portfolio dataset created to demonstrate analytics workflows. "
    "Metrics should not be represented as actual company results."
)
