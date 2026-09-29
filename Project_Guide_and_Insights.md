# Supply Chain & Inventory Optimization Analytics
## Portfolio project pack

**Important:** All records are synthetic and designed for a portfolio demonstration. Do not present them as actual employer/company results.

## Project objective
Use Excel, SQL and Power BI to monitor delivery reliability, inventory risk, supplier performance and revenue/margin trends. Translate the analysis into operational actions.

## Data included
- `Order_Fact`: 1,200 order lines across 2025, with SKU, warehouse, region, channel, quantities, promised/actual lead time and unit economics.
- `Inventory_Snapshot`: current-style snapshot for 12 SKUs, including reorder point, safety stock and inventory value.
- `Supplier_Scorecard`: four supplier profiles with lead time, on-time rate, defect rate and spend.
- `KPI_Summary`: precomputed KPI summary.

## Calculated headline metrics from this dataset
- **1,200 order lines** analyzed during 2025.
- **27,246 units delivered**.
- **₹32,806,800 recognized revenue** based on delivered units.
- **₹12,118,172 gross profit** before operating expenses.
- **51% on-time and complete order-line rate** (rounded).
- **549 order lines** had actual lead time above the promised days.
- **76 order lines** were partially fulfilled.
- **5 of 12 SKUs** need attention; **4** are at/below reorder point.
- Inventory snapshot value: **₹1,010,324** at recorded unit cost.
- Highest revenue category: **Electronics**.
- Warehouse with highest late-order share: **Aurangabad**.
- Highest revenue product: **Mechanical Keyboard**.

## Business insights to say in an interview
1. **Service reliability:** 549 of 1,200 order lines exceeded promised lead time. Segment by warehouse and month to isolate where delays cluster before changing carrier or staffing plans.
2. **Fulfilment completeness:** 76 order lines were short-shipped. Compare partial fulfilment by SKU and category to identify whether inventory availability or picking/dispatch processes need review.
3. **Inventory control:** 5 of 12 SKUs are not marked healthy. Prioritize the `Reorder Now` SKUs using inventory position (on-hand + on-order) versus reorder point, rather than looking only at on-hand stock.
4. **Commercial focus:** Electronics is the largest revenue category in this dataset. Compare its gross margin and delivery performance before prioritizing additional stock.
5. **Warehouse action:** Aurangabad has the highest late-order share in this sample. Validate order volume, product mix and supplier lead times before concluding that the warehouse itself is the cause.

## Power BI report design (3 pages)
### Page 1 — Executive Overview
- KPI cards: Revenue, Gross Profit, Units Delivered, On-Time & Complete %, Fill Rate %.
- Monthly line chart: Revenue by month.
- Clustered bar: Revenue and gross profit by category.
- Stacked bar: Order status by warehouse.
- Slicers: date, region, warehouse, category, sales channel.

### Page 2 — Inventory & Replenishment
- KPI cards: Inventory Value, SKUs Reorder Now, SKUs Needing Attention.
- Table: SKU, product, on-hand, on-order, safety stock, reorder point, action status.
- Bar chart: on-hand vs reorder point by SKU.
- Scatter: average daily demand vs supplier lead time.
- Conditional formatting: red for Reorder Now, amber for Low Stock, green for Healthy.

### Page 3 — Delivery & Supplier Performance
- KPI cards: On-Time & Complete %, Late Orders, average actual lead days.
- Bar chart: late delivery % by warehouse.
- Trend: monthly late delivery %.
- Supplier table: on-time %, defect %, lead time, spend.
- Drill-through: SKU or warehouse details.

## SQL / Excel / Power BI workflow
1. Open the workbook and import the four sheets into SQL tables using the names in `analysis_queries.sql`.
2. Run SQL queries to validate KPIs, monthly trends, warehouse delays, supplier performance and reorder alerts.
3. In Power BI Desktop, import the Excel workbook, set `Order_Date` to Date and numeric columns to appropriate number/currency types.
4. Create measures from `PowerBI_DAX_Measures.txt`; format revenue/profit as INR and percentages as %.
5. Build the three report pages above. Add a note on the report: "Portfolio demo — synthetic dataset."
6. Validate that totals match between SQL and Power BI before publishing.

## Resume bullet
Built a Supply Chain & Inventory Optimization Analytics solution using SQL, Excel and Power BI to analyze 1,200 synthetic order lines, delivery SLA performance, SKU-level reorder risk, supplier service and gross margin; designed KPI dashboards and actionable replenishment insights.

## Interview explanation (30 seconds)
"I built an end-to-end supply chain analytics project using SQL, Excel and Power BI. I analyzed 1,200 order lines to measure revenue, gross profit, delivery SLA performance and fulfilment rates, then combined that with SKU inventory and supplier scorecards. The dashboard helps an operations team identify delayed deliveries, prioritize reorder alerts and compare supplier reliability. The dataset is synthetic, so the numbers demonstrate the analysis workflow rather than real company performance."
