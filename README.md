# Supply Chain Control Tower — Streamlit

## Deploy directly
1. Upload `app.py` and `requirements.txt` to a GitHub repository.
2. Open https://share.streamlit.io/
3. Choose the repository and select `app.py` as the main file.
4. Click Deploy.

No separate Excel dataset is required: the app generates a reproducible synthetic demo dataset automatically. You can optionally upload an Excel workbook with `Order_Fact`, `Inventory_Snapshot`, and `Supplier_Scorecard` sheets in the sidebar.

## Dashboard
- 7 KPI cards: Revenue, Gross Profit, Units Delivered, On-Time & Complete, Fill Rate, Late Order Lines, SKUs to Reorder
- Executive overview with revenue trends, category contribution, fulfilment status and warehouse performance
- Inventory health, reorder points, safety stock and replenishment action list
- Delivery performance and supplier scorecard
- Interactive filters and CSV export

**Data note:** Built-in metrics use synthetic portfolio data and must not be represented as actual company results.
