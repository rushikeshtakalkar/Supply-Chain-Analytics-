# One-page Power BI dashboard: Supply Chain Control Tower

## 1) Load data
Power BI Desktop → Get Data → Excel → select `Supply_Chain_Inventory_Analytics.xlsx`.
Load sheets:
- `Order_Fact`
- `Inventory_Snapshot`
- `Supplier_Scorecard`

Set `Order_Date` to Date data type. Set quantity, days and INR fields to numeric types.

## 2) Create model relationship
The supplied workbook has one row per SKU in Inventory_Snapshot and many order lines per SKU in Order_Fact.
Create relationship:
`Inventory_Snapshot[SKU]` (one) → `Order_Fact[SKU]` (many).
Use single-direction filtering from Inventory_Snapshot to Order_Fact. If the model gives ambiguity, create a separate SKU dimension instead.

## 3) Single-page layout (16:9)
Canvas: 1280 x 720, white/light background, navy header, teal accent, consistent spacing.

Header (height ~70):
- Title: SUPPLY CHAIN CONTROL TOWER
- Subtitle: Service level | Inventory health | Commercial performance
- Right: last refresh date (optional)

KPI row (7 cards, same width):
1. Revenue (INR)
2. Gross Profit (INR)
3. Units Delivered
4. On-Time & Complete %
5. Fill Rate %
6. Late Order Lines
7. SKUs to Reorder

Middle row:
- Left 60%: line chart, Month on X axis, Revenue (INR) on Y axis
- Right 40%: bar chart, Category on axis, Revenue and Gross Profit as values

Bottom row:
- Left 50%: bar chart, Warehouse by Late Delivery %
- Right 50%: inventory table with Product, On_Hand_Units, On_Order_Units, Reorder_Point_Units, Stock_Status

Slicers across top or left:
- Order_Date
- Region
- Warehouse
- Category
- Sales_Channel

## 4) Visual setup
- Format revenue/profit as INR currency with display units = Millions or Crores.
- Format On-Time & Complete % and Fill Rate % as percentage with 1 decimal.
- Sort monthly trend by Order_Date, not alphabetically by month text.
- Apply conditional formatting to Stock_Status: Reorder Now = red, Low Stock = amber, Healthy = green.
- Enable report-page tooltips for the KPI cards if desired.
- Avoid too many borders, shadows and different colours; use one navy, one teal and neutral greys.

## 5) Business insight text box
Use a dynamic or manually updated text box only after checking filtered results:
- “Late order lines: [Late Order Lines]. Review warehouse and product mix to identify delivery bottlenecks.”
- “Reorder alerts: [SKUs to Reorder] SKUs are at or below reorder point based on the supplied snapshot.”
- “Fill rate: [Fill Rate %] of ordered units were delivered.”
Do not assert that a specific operational issue caused delays unless the data supports it.

## 6) Resume bullet
Built a one-page Supply Chain Control Tower in Power BI using SQL-style KPI logic and Excel data to monitor revenue, gross profit, delivery SLA, fill rate and SKU replenishment risk through interactive filters and operational visuals.

## Data disclosure
The project workbook contains synthetic portfolio data. State this clearly in the report or project README; do not present the figures as actual company results.
