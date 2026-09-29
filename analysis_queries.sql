-- Supply Chain & Inventory Optimization Analytics
-- SQL dialect: PostgreSQL / broadly portable SQL
-- Dataset note: synthetic portfolio dataset; import Excel sheets as tables:
-- order_fact, inventory_snapshot, supplier_scorecard

-- 1. Executive KPIs: revenue, delivered units, order count, on-time-complete %
SELECT
  COUNT(*) AS order_lines,
  SUM(delivered_qty) AS units_delivered,
  SUM(delivered_qty * unit_price_inr) AS revenue_inr,
  SUM(delivered_qty * (unit_price_inr - unit_cost_inr)) AS gross_profit_inr,
  ROUND(100.0 * AVG(CASE
    WHEN actual_lead_days <= promised_days AND delivered_qty = order_qty THEN 1.0
    ELSE 0.0 END), 2) AS on_time_complete_pct
FROM order_fact;

-- 2. Monthly trend: revenue and late delivery rate
SELECT DATE_TRUNC('month', order_date)::date AS month,
       SUM(delivered_qty * unit_price_inr) AS revenue_inr,
       ROUND(100.0 * AVG(CASE WHEN actual_lead_days > promised_days THEN 1.0 ELSE 0.0 END), 2) AS late_order_pct
FROM order_fact
GROUP BY 1
ORDER BY 1;

-- 3. Category contribution and gross margin
SELECT category,
       SUM(delivered_qty * unit_price_inr) AS revenue_inr,
       SUM(delivered_qty * (unit_price_inr - unit_cost_inr)) AS gross_profit_inr,
       ROUND(100.0 * SUM(delivered_qty * (unit_price_inr-unit_cost_inr))
         / NULLIF(SUM(delivered_qty * unit_price_inr),0), 2) AS gross_margin_pct
FROM order_fact
GROUP BY category
ORDER BY revenue_inr DESC;

-- 4. Warehouse service performance
SELECT warehouse,
       COUNT(*) AS order_lines,
       ROUND(100.0 * AVG(CASE WHEN actual_lead_days > promised_days THEN 1.0 ELSE 0.0 END),2) AS late_delivery_pct,
       ROUND(100.0 * AVG(CASE WHEN delivered_qty = order_qty THEN 1.0 ELSE 0.0 END),2) AS complete_fill_pct,
       AVG(actual_lead_days) AS avg_lead_days
FROM order_fact
GROUP BY warehouse
ORDER BY late_delivery_pct DESC;

-- 5. SKU reorder alerts using inventory position (on-hand + on-order)
SELECT sku, product, warehouse, on_hand_units, on_order_units,
       reorder_point_units, safety_stock_units,
       CASE WHEN on_hand_units + on_order_units <= reorder_point_units THEN 'REORDER NOW'
            WHEN on_hand_units <= safety_stock_units THEN 'LOW STOCK'
            ELSE 'HEALTHY' END AS action_status
FROM inventory_snapshot
WHERE on_hand_units + on_order_units <= reorder_point_units
   OR on_hand_units <= safety_stock_units
ORDER BY (reorder_point_units - (on_hand_units + on_order_units)) DESC;

-- 6. Supplier scorecard: identify service/quality risk
SELECT supplier, category, avg_lead_time_days, on_time_delivery_pct,
       defect_rate_pct, spend_inr
FROM supplier_scorecard
ORDER BY on_time_delivery_pct ASC, defect_rate_pct DESC;

-- 7. ABC-style product prioritization by revenue contribution
WITH sku_revenue AS (
  SELECT sku, product, SUM(delivered_qty * unit_price_inr) AS revenue_inr
  FROM order_fact GROUP BY sku, product
), ranked AS (
  SELECT *, SUM(revenue_inr) OVER (ORDER BY revenue_inr DESC)
             / NULLIF(SUM(revenue_inr) OVER (),0) AS cumulative_revenue_share
  FROM sku_revenue
)
SELECT sku, product, revenue_inr,
       ROUND(100.0 * cumulative_revenue_share,2) AS cumulative_revenue_share_pct,
       CASE WHEN cumulative_revenue_share <= 0.80 THEN 'A'
            WHEN cumulative_revenue_share <= 0.95 THEN 'B'
            ELSE 'C' END AS abc_class
FROM ranked ORDER BY revenue_inr DESC;
