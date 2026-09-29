import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Supply Chain Control Tower",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(31,78,121,.10), rgba(38,166,154,.08));
    border: 1px solid rgba(120,140,160,.25);
    padding: 14px 16px; border-radius: 14px;
}
div[data-testid="stMetricLabel"] {font-size: .85rem;}
div[data-testid="stMetricValue"] {font-size: 1.65rem;}
.small-note {font-size: 12px; color: #77808b;}
</style>
""", unsafe_allow_html=True)

# ---------- Data ----------
@st.cache_data
def make_demo_data():
    """Reproducible synthetic portfolio dataset. No external files required."""
    rng = np.random.default_rng(17)
    n = 1600
    dates = pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, n), unit="D")
    catalog = [
        ("SKU-1001", "Wireless Mouse", "Electronics", "Pune", 420, 260),
        ("SKU-1002", "USB-C Hub", "Electronics", "Mumbai", 1450, 920),
        ("SKU-1003", "Laptop Stand", "Accessories", "Nagpur", 980, 610),
        ("SKU-1004", "Mechanical Keyboard", "Electronics", "Pune", 2750, 1780),
        ("SKU-1005", "HDMI Cable", "Accessories", "Nashik", 320, 155),
        ("SKU-1006", "Webcam 1080p", "Electronics", "Mumbai", 1850, 1210),
        ("SKU-1007", "Notebook Pack", "Office Supplies", "Pune", 180, 78),
        ("SKU-1008", "Desk Organizer", "Office Supplies", "Aurangabad", 540, 290),
        ("SKU-1009", "Power Bank", "Electronics", "Nagpur", 1250, 810),
        ("SKU-1010", "Bluetooth Speaker", "Electronics", "Nashik", 1650, 1030),
        ("SKU-1011", "Monitor Arm", "Accessories", "Mumbai", 2200, 1460),
        ("SKU-1012", "Ethernet Adapter", "Electronics", "Pune", 650, 360),
    ]
    regions = ["West", "South", "North", "Central"]
    channels = ["B2B", "Online", "Retail"]
    rows = []
    for i in range(n):
        p = catalog[int(rng.integers(0, len(catalog)))]
        qty = int(rng.integers(4, 55))
        month = pd.Timestamp(dates[i]).month
        promised = int(rng.integers(3, 9))
        lead = max(1, int(round(rng.normal(5.0, 2.3) + (1.8 if rng.random() < .14 else 0))))
        short = int(rng.choice([0, 0, 0, 0, 1, 2], p=[.70, .08, .06, .04, .07, .05]))
        delivered = max(0, qty - short)
        if delivered < qty:
            status = "Partially Delivered"
        elif lead > promised:
            status = "Delayed"
        else:
            status = "Delivered"
        rows.append({
            "Order_ID": f"ORD-{i+1:05d}",
            "Order_Date": pd.Timestamp(dates[i]),
            "SKU": p[0], "Product": p[1], "Category": p[2], "Warehouse": p[3],
            "Region": str(rng.choice(regions)), "Sales_Channel": str(rng.choice(channels)),
            "Order_Qty": qty, "Delivered_Qty": delivered,
            "Unit_Price_INR": p[4], "Unit_Cost_INR": p[5],
            "Promised_Days": promised, "Actual_Lead_Days": lead,
            "Order_Status": status,
        })
    orders = pd.DataFrame(rows)
    orders["Revenue_INR"] = orders["Delivered_Qty"] * orders["Unit_Price_INR"]
    orders["COGS_INR"] = orders["Delivered_Qty"] * orders["Unit_Cost_INR"]
    orders["Gross_Profit_INR"] = orders["Revenue_INR"] - orders["COGS_INR"]
    orders["Late_Flag"] = orders["Actual_Lead_Days"] > orders["Promised_Days"]
    orders["On_Time_Complete_Flag"] = (
        (~orders["Late_Flag"]) & (orders["Delivered_Qty"] == orders["Order_Qty"])
    )
    orders["Fill_Rate"] = orders["Delivered_Qty"] / orders["Order_Qty"]

    inv_rows = []
    for p in catalog:
        daily = float(rng.integers(4, 16))
        on_hand = int(rng.integers(25, 240))
        on_order = int(rng.integers(0, 90))
        lead = int(rng.integers(3, 13))
        safety = int(round(daily * int(rng.integers(4, 9))))
        reorder = int(round(daily * lead + safety))
        position = on_hand + on_order
        status = "Reorder Now" if position <= reorder else ("Low Stock" if on_hand <= safety else "Healthy")
        inv_rows.append({
            "SKU": p[0], "Product": p[1], "Category": p[2], "Warehouse": p[3],
            "On_Hand_Units": on_hand, "On_Order_Units": on_order,
            "Avg_Daily_Demand_Units": round(daily, 1), "Supplier_Lead_Time_Days": lead,
            "Safety_Stock_Units": safety, "Reorder_Point_Units": reorder,
            "Inventory_Position": position, "Inventory_Value_INR": on_hand * p[5],
            "Stock_Status": status,
        })
    inventory = pd.DataFrame(inv_rows)
    suppliers = pd.DataFrame([
        {"Supplier":"Apex Components","Category":"Electronics","Avg_Lead_Time_Days":6.2,"On_Time_Delivery_Pct":91.5,"Defect_Rate_Pct":1.8,"Spend_INR":1250000},
        {"Supplier":"Westline Distribution","Category":"Accessories","Avg_Lead_Time_Days":8.4,"On_Time_Delivery_Pct":84.2,"Defect_Rate_Pct":2.6,"Spend_INR":890000},
        {"Supplier":"Metro Office Supply","Category":"Office Supplies","Avg_Lead_Time_Days":4.7,"On_Time_Delivery_Pct":96.1,"Defect_Rate_Pct":0.9,"Spend_INR":420000},
        {"Supplier":"Nova Electronics","Category":"Electronics","Avg_Lead_Time_Days":7.1,"On_Time_Delivery_Pct":88.7,"Defect_Rate_Pct":2.1,"Spend_INR":970000},
    ])
    return orders, inventory, suppliers

orders, inventory, suppliers = make_demo_data()

# Optional real/demo workbook override
with st.sidebar:
    st.markdown("## Control filters")
    upload = st.file_uploader("Optional: use your own Excel workbook", type=["xlsx"])
    if upload is not None:
        try:
            orders = pd.read_excel(upload, sheet_name="Order_Fact")
            inventory = pd.read_excel(upload, sheet_name="Inventory_Snapshot")
            suppliers = pd.read_excel(upload, sheet_name="Supplier_Scorecard")
            orders["Order_Date"] = pd.to_datetime(orders["Order_Date"], errors="coerce")
            orders["Revenue_INR"] = orders["Delivered_Qty"] * orders["Unit_Price_INR"]
            orders["Gross_Profit_INR"] = orders["Delivered_Qty"] * (orders["Unit_Price_INR"] - orders["Unit_Cost_INR"])
            orders["Late_Flag"] = orders["Actual_Lead_Days"] > orders["Promised_Days"]
            orders["On_Time_Complete_Flag"] = (~orders["Late_Flag"]) & (orders["Delivered_Qty"] == orders["Order_Qty"])
            orders["Fill_Rate"] = orders["Delivered_Qty"] / orders["Order_Qty"].replace(0, np.nan)
            if "Inventory_Position" not in inventory.columns:
                inventory["Inventory_Position"] = inventory["On_Hand_Units"] + inventory["On_Order_Units"]
        except Exception as e:
            st.error(f"Workbook could not be loaded. Using built-in demo data. Details: {e}")
            orders, inventory, suppliers = make_demo_data()

    date_min, date_max = orders["Order_Date"].min().date(), orders["Order_Date"].max().date()
    date_range = st.date_input("Order date", value=(date_min, date_max), min_value=date_min, max_value=date_max)
    region_opts = sorted(orders["Region"].dropna().unique())
    warehouse_opts = sorted(orders["Warehouse"].dropna().unique())
    category_opts = sorted(orders["Category"].dropna().unique())
    channel_opts = sorted(orders["Sales_Channel"].dropna().unique())
    sel_regions = st.multiselect("Region", region_opts, default=region_opts)
    sel_warehouses = st.multiselect("Warehouse", warehouse_opts, default=warehouse_opts)
    sel_categories = st.multiselect("Category", category_opts, default=category_opts)
    sel_channels = st.multiselect("Sales channel", channel_opts, default=channel_opts)

filtered = orders[
    orders["Region"].isin(sel_regions)
    & orders["Warehouse"].isin(sel_warehouses)
    & orders["Category"].isin(sel_categories)
    & orders["Sales_Channel"].isin(sel_channels)
].copy()
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    filtered = filtered[filtered["Order_Date"].dt.date.between(date_range[0], date_range[1])]

st.title("📦 Supply Chain Control Tower")
st.markdown("**Supply Chain & Inventory Optimization Analytics**  ·  Operations performance overview")
st.caption("Portfolio demonstration using a reproducible synthetic dataset. Filters update the KPIs and charts.")

if filtered.empty:
    st.warning("No records match the selected filters. Please widen the filters.")
    st.stop()

# ---------- 7 KPIs ----------
order_lines = filtered["Order_ID"].nunique()
units_ordered = filtered["Order_Qty"].sum()
units_delivered = filtered["Delivered_Qty"].sum()
revenue = filtered["Revenue_INR"].sum()
profit = filtered["Gross_Profit_INR"].sum()
on_time = filtered["On_Time_Complete_Flag"].mean()
fill_rate = units_delivered / units_ordered if units_ordered else 0
late_orders = int(filtered["Late_Flag"].sum())
gross_margin = profit / revenue if revenue else 0
inventory_value = inventory["Inventory_Value_INR"].sum()
reorder_count = int((inventory["Stock_Status"] == "Reorder Now").sum())
attention_count = int((inventory["Stock_Status"] != "Healthy").sum())

kpis = [
    ("Revenue", f"₹{revenue/1e7:.2f} Cr", f"₹{revenue:,.0f} total"),
    ("Gross Profit", f"₹{profit/1e7:.2f} Cr", f"{gross_margin:.1%} gross margin"),
    ("Units Delivered", f"{units_delivered:,.0f}", f"of {units_ordered:,.0f} ordered"),
    ("On-Time & Complete", f"{on_time:.1%}", "order lines meeting both conditions"),
    ("Fill Rate", f"{fill_rate:.1%}", "delivered units ÷ ordered units"),
    ("Late Order Lines", f"{late_orders:,}", f"{late_orders/max(order_lines,1):.1%} of filtered lines"),
    ("SKUs to Reorder", f"{reorder_count}", f"{attention_count} of {len(inventory)} SKUs need attention"),
]
cols = st.columns(7)
for col, (label, value, help_text) in zip(cols, kpis):
    col.metric(label, value, help=help_text)

st.divider()
overview, inventory_tab, delivery_tab, data_tab = st.tabs([
    "📈 Executive Overview", "📦 Inventory & Replenishment",
    "🚚 Delivery & Suppliers", "🔎 Order Explorer"
])

with overview:
    c1, c2 = st.columns([1.4, 1])
    monthly = filtered.assign(Month=filtered["Order_Date"].dt.to_period("M").astype(str)).groupby("Month", as_index=False).agg(
        Revenue=("Revenue_INR", "sum"), Gross_Profit=("Gross_Profit_INR", "sum"))
    with c1:
        st.subheader("Revenue trend")
        fig = px.line(monthly, x="Month", y="Revenue", markers=True)
        fig.update_traces(line_width=3)
        fig.update_layout(xaxis_title=None, yaxis_title="Revenue (₹)", margin=dict(t=15, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Revenue by category")
        cat = filtered.groupby("Category", as_index=False).agg(Revenue=("Revenue_INR","sum"), Gross_Profit=("Gross_Profit_INR","sum"))
        fig = px.bar(cat.sort_values("Revenue"), x="Revenue", y="Category", orientation="h", text_auto=".2s")
        fig.update_layout(xaxis_title="Revenue (₹)", yaxis_title=None, margin=dict(t=15,b=10))
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Order fulfilment status")
        status = filtered["Order_Status"].value_counts().rename_axis("Status").reset_index(name="Order Lines")
        fig = px.pie(status, names="Status", values="Order Lines", hole=.52)
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        st.subheader("Warehouse performance")
        wh = filtered.groupby("Warehouse", as_index=False).agg(
            Order_Lines=("Order_ID","count"), Late_Rate=("Late_Flag","mean"), Revenue=("Revenue_INR","sum"))
        wh["Late Rate (%)"] = wh["Late_Rate"] * 100
        fig = px.bar(wh.sort_values("Late Rate (%)"), x="Warehouse", y="Late Rate (%)", text_auto=".1f")
        fig.update_layout(yaxis_title="Late order lines (%)", xaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Decision notes")
    partial_count = int((filtered["Delivered_Qty"] < filtered["Order_Qty"]).sum())
    worst_wh = wh.sort_values("Late Rate (%)", ascending=False).iloc[0]
    top_cat = cat.sort_values("Revenue", ascending=False).iloc[0]
    st.markdown(
        f"- **Delivery exception:** {late_orders:,} of {order_lines:,} filtered order lines exceeded promised lead time. "
        f"Review warehouse, SKU mix and supplier lead time before assigning root cause.\n"
        f"- **Short fulfilment:** {partial_count:,} order lines delivered fewer units than ordered; investigate stock availability and picking/dispatch records.\n"
        f"- **Revenue concentration:** {top_cat['Category']} is the largest revenue category in the current filter, at **₹{top_cat['Revenue']:,.0f}**.\n"
        f"- **Warehouse follow-up:** {worst_wh['Warehouse']} shows the highest late-order share in the current filter (**{worst_wh['Late Rate (%)']:.1f}%**); validate the sample and operational context."
    )

with inventory_tab:
    st.subheader("Inventory health")
    inv = inventory.copy()
    if "Inventory_Position" not in inv.columns:
        inv["Inventory_Position"] = inv["On_Hand_Units"] + inv["On_Order_Units"]
    inv["Reorder_Gap"] = inv["Reorder_Point_Units"] - inv["Inventory_Position"]
    i1, i2, i3 = st.columns(3)
    i1.metric("Inventory value", f"₹{inventory_value:,.0f}")
    i2.metric("Reorder now", f"{reorder_count} SKUs")
    i3.metric("Needs attention", f"{attention_count} SKUs")
    left, right = st.columns(2)
    with left:
        st.subheader("On-hand stock vs reorder point")
        chart_data = inv.melt(id_vars="Product", value_vars=["On_Hand_Units","Reorder_Point_Units"], var_name="Measure", value_name="Units")
        fig = px.bar(chart_data, x="Product", y="Units", color="Measure", barmode="group")
        fig.update_layout(xaxis_title=None, xaxis_tickangle=-35)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Stock status")
        stock_status = inv["Stock_Status"].value_counts().rename_axis("Status").reset_index(name="SKUs")
        fig = px.pie(stock_status, names="Status", values="SKUs", hole=.48)
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("Replenishment action list")
    view = inv[["SKU","Product","Category","Warehouse","On_Hand_Units","On_Order_Units","Inventory_Position","Safety_Stock_Units","Reorder_Point_Units","Reorder_Gap","Inventory_Value_INR","Stock_Status"]].sort_values("Reorder_Gap", ascending=False)
    st.dataframe(view, use_container_width=True, hide_index=True)

with delivery_tab:
    st.subheader("Delivery service levels")
    wh = filtered.groupby("Warehouse", as_index=False).agg(
        Order_Lines=("Order_ID","count"), Late_Orders=("Late_Flag","sum"),
        Avg_Lead_Days=("Actual_Lead_Days","mean"),
        On_Time_Complete=("On_Time_Complete_Flag","mean"))
    wh["Late Rate (%)"] = 100 * wh["Late_Orders"] / wh["Order_Lines"]
    wh["On-Time & Complete (%)"] = 100 * wh["On_Time_Complete"]
    left, right = st.columns(2)
    with left:
        fig = px.bar(wh.sort_values("Late Rate (%)", ascending=False), x="Warehouse", y="Late Rate (%)", text_auto=".1f")
        fig.update_layout(xaxis_title=None, yaxis_title="Late order lines (%)")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        trend = filtered.assign(Month=filtered["Order_Date"].dt.to_period("M").astype(str)).groupby("Month", as_index=False).agg(
            Late_Rate=("Late_Flag","mean"))
        trend["Late Rate (%)"] = trend["Late_Rate"] * 100
        fig = px.line(trend, x="Month", y="Late Rate (%)", markers=True)
        fig.update_layout(xaxis_title=None, yaxis_title="Late order lines (%)")
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("Supplier scorecard")
    st.dataframe(suppliers.sort_values("On_Time_Delivery_Pct", ascending=False), use_container_width=True, hide_index=True)
    st.caption("Supplier metrics are illustrative inputs in the demo dataset; they are not derived from the order table.")

with data_tab:
    st.subheader("Filtered order records")
    st.write(f"Showing **{len(filtered):,}** order lines.")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Download filtered data (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="supply_chain_filtered_orders.csv",
        mime="text/csv",
    )

st.divider()
st.markdown(
    '<div class="small-note">Portfolio demo • The built-in data is synthetic and reproducible. '
    'Do not represent the displayed metrics as actual company results.</div>',
    unsafe_allow_html=True,
)
