-- Query 1: Core Product Performance Matrix
-- Evaluate sales velocity, volume, and total net yield
SELECT p.product_name, p.unit_price, COUNT(f.order_id) AS transaction_count, SUM(f.quantity) AS total_units_sold, ROUND(SUM(f.net_revenue), 2) AS total_net_revenue
FROM fact_orders f JOIN dim_products p ON f.product_name = p.product_name
GROUP BY p.product_name
ORDER BY total_net_revenue DESC;

-- Query 2: Longitudinal User Purchase Trajectory
-- Track repeat buyer patterns and acceleration of spend
SELECT user_id, order_id, order_timestamp, net_revenue, 
    -- Pulls net revenue of user's immediate prior order to check behavior changes 
    LAG(net_revenue, 1) OVER (PARTITION BY user_id ORDER BY order_timestamp) AS previous_order_value, 
    -- Dynamically tallies a user's running total expenditure across the 60-day window
    ROUND(SUM(net_revenue) OVER (PARTITION BY user_id ORDER BY order_timestamp), 2) AS cumulative_user_spend
FROM fact_orders;

-- Query 3: Highest Single-Day Revenue
-- Isolate peak revenue dates to idenitify spikes
WITH daily_revenue_summary AS (
    SELECT DATE(order_timestamp) AS order_date, ROUND(SUM(net_revenue), 2) AS total_daily_revenue, COUNT(order_id) AS daily_order_volume
    FROM fact_orders
    GROUP BY DATE(order_timestamp)
)
SELECT order_date, total_daily_revenue, daily_order_volume
FROM daily_revenue_summary
WHERE total_daily_revenue > (
    SELECT AVG(total_daily_revenue)
    FROM daily_revenue_summary
)
ORDER BY total_daily_revenue DESC;
