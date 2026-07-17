/* =========================================================================
   BLINKIT ORDER ANALYTICS – SQL ANALYSIS
   Table: blinkit_orders  (load blinkit_orders.csv into this table first)
   Dialect: PostgreSQL / MySQL compatible (window functions, CTEs used)
   =========================================================================
   Business problem: Blinkit is seeing rising order cancellations and
   inconsistent delivery times, which hurts repeat usage and revenue.
   These queries build the evidence base for that story: revenue health,
   customer behaviour, delivery performance, and profitability.
   ========================================================================= */

-- Suggested table definition (adjust types to your DB engine)
-- CREATE TABLE blinkit_orders (
--   Order_ID TEXT, Customer_ID TEXT, City TEXT, Area TEXT, Store_ID TEXT,
--   Product_Category TEXT, Product_Name TEXT, Quantity INT,
--   Selling_Price NUMERIC, Discount NUMERIC, Delivery_Fee NUMERIC,
--   Delivery_Time_Min NUMERIC, Order_Time TEXT, Order_Date DATE,
--   Payment_Method TEXT, Delivery_Partner TEXT, Order_Status TEXT,
--   Customer_Rating NUMERIC, Customer_Type TEXT, Coupon_Used TEXT,
--   App_Version TEXT, Device_Type TEXT, Platform TEXT,
--   Session_Duration_Min NUMERIC, Cart_Value NUMERIC,
--   Final_Order_Value NUMERIC, Profit NUMERIC, Marketing_Channel TEXT
-- );


-- =========================================================================
-- SECTION 1: REVENUE & SALES OVERVIEW
-- =========================================================================

-- Q1. Total revenue, orders, and average order value (delivered orders only)
SELECT
    COUNT(*)                           AS total_orders,
    SUM(Final_Order_Value)             AS total_revenue,
    ROUND(AVG(Final_Order_Value), 2)   AS avg_order_value
FROM blinkit_orders
WHERE Order_Status = 'Delivered';
-- Insight: Gives the single top-line number leadership tracks every week.
-- AOV benchmarks whether basket-building tactics (cross-sell, bundles) are working.


-- Q2. Monthly revenue trend
SELECT
    DATE_TRUNC('month', Order_Date) AS order_month,
    SUM(Final_Order_Value)          AS revenue,
    COUNT(*)                        AS orders
FROM blinkit_orders
WHERE Order_Status = 'Delivered'
GROUP BY 1
ORDER BY 1;
-- Insight: Reveals seasonality (e.g. festive-month spikes) so marketing and
-- inventory can plan ahead instead of reacting to demand surges.


-- Q3. Month-over-month revenue growth using window function
WITH monthly AS (
    SELECT DATE_TRUNC('month', Order_Date) AS order_month,
           SUM(Final_Order_Value) AS revenue
    FROM blinkit_orders
    WHERE Order_Status = 'Delivered'
    GROUP BY 1
)
SELECT
    order_month,
    revenue,
    LAG(revenue) OVER (ORDER BY order_month) AS prev_month_revenue,
    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY order_month))
        / NULLIF(LAG(revenue) OVER (ORDER BY order_month), 0), 2
    ) AS mom_growth_pct
FROM monthly
ORDER BY order_month;
-- Insight: MoM growth is more actionable than absolute revenue — flags
-- exactly which month growth stalled or accelerated.


-- Q4. Revenue and order share by product category
SELECT
    Product_Category,
    COUNT(*)                                        AS orders,
    SUM(Final_Order_Value)                           AS revenue,
    ROUND(100.0 * SUM(Final_Order_Value)
        / SUM(SUM(Final_Order_Value)) OVER (), 2)    AS revenue_share_pct
FROM blinkit_orders
WHERE Order_Status = 'Delivered'
GROUP BY Product_Category
ORDER BY revenue DESC;
-- Insight: Identifies which categories to protect (top revenue drivers)
-- vs. which are underperforming and could be trimmed or promoted.


-- Q5. Top 10 best-selling products by quantity
SELECT
    Product_Name,
    Product_Category,
    SUM(Quantity)            AS total_units_sold,
    SUM(Final_Order_Value)   AS revenue
FROM blinkit_orders
WHERE Order_Status = 'Delivered'
GROUP BY Product_Name, Product_Category
ORDER BY total_units_sold DESC
LIMIT 10;
-- Insight: Guides inventory prioritisation — these SKUs must never go out of stock.


-- =========================================================================
-- SECTION 2: CUSTOMER SEGMENTATION & RETENTION
-- =========================================================================

-- Q6. Orders and revenue by customer type
SELECT
    Customer_Type,
    COUNT(DISTINCT Customer_ID) AS customers,
    COUNT(*)                    AS orders,
    SUM(Final_Order_Value)      AS revenue,
    ROUND(AVG(Final_Order_Value), 2) AS avg_order_value
FROM blinkit_orders
WHERE Order_Status = 'Delivered'
GROUP BY Customer_Type
ORDER BY revenue DESC;
-- Insight: Loyal customers usually drive disproportionate revenue relative
-- to their headcount — quantifies the ROI of retention programs.


-- Q7. Repeat customers: number of orders per customer
SELECT
    Customer_ID,
    COUNT(*) AS total_orders,
    SUM(Final_Order_Value) AS lifetime_value
FROM blinkit_orders
WHERE Order_Status = 'Delivered'
GROUP BY Customer_ID
HAVING COUNT(*) > 1
ORDER BY total_orders DESC;
-- Insight: Size of the repeat-buyer base indicates habit formation —
-- core to a quick-commerce growth thesis.


-- Q8. Repeat purchase rate (%)
WITH customer_orders AS (
    SELECT Customer_ID, COUNT(*) AS orders
    FROM blinkit_orders
    WHERE Order_Status = 'Delivered'
    GROUP BY Customer_ID
)
SELECT
    COUNT(*) FILTER (WHERE orders > 1) AS repeat_customers,
    COUNT(*)                            AS total_customers,
    ROUND(100.0 * COUNT(*) FILTER (WHERE orders > 1) / COUNT(*), 2) AS repeat_rate_pct
FROM customer_orders;
-- Insight: The single clearest KPI for "is retention actually a problem?" —
-- ties directly back to the business problem statement.


-- Q9. Customer ranking by lifetime value using RANK()
SELECT
    Customer_ID,
    SUM(Final_Order_Value) AS lifetime_value,
    RANK() OVER (ORDER BY SUM(Final_Order_Value) DESC) AS value_rank
FROM blinkit_orders
WHERE Order_Status = 'Delivered'
GROUP BY Customer_ID
ORDER BY value_rank
LIMIT 20;
-- Insight: Identifies top-20 high-value customers for a VIP retention or
-- referral program.


-- Q10. New vs. Returning vs. Loyal customer monthly mix
SELECT
    DATE_TRUNC('month', Order_Date) AS order_month,
    Customer_Type,
    COUNT(*) AS orders
FROM blinkit_orders
WHERE Order_Status = 'Delivered'
GROUP BY 1, 2
ORDER BY 1, 2;
-- Insight: Tracks whether new-customer acquisition is converting into
-- returning/loyal cohorts over time, or leaking away after one order.


-- Q11. Customer segmentation by spend (RFM-style bucket, simplified)
SELECT
    Customer_ID,
    SUM(Final_Order_Value) AS total_spend,
    CASE
        WHEN SUM(Final_Order_Value) >= 5000 THEN 'High Value'
        WHEN SUM(Final_Order_Value) >= 1500 THEN 'Mid Value'
        ELSE 'Low Value'
    END AS spend_segment
FROM blinkit_orders
WHERE Order_Status = 'Delivered'
GROUP BY Customer_ID;
-- Insight: Simple, explainable segmentation that marketing can act on
-- without needing a full RFM/clustering model.


-- =========================================================================
-- SECTION 3: DELIVERY PERFORMANCE
-- =========================================================================

-- Q12. Average delivery time by city
SELECT
    City,
    ROUND(AVG(Delivery_Time_Min), 2) AS avg_delivery_time,
    COUNT(*) AS orders
FROM blinkit_orders
GROUP BY City
ORDER BY avg_delivery_time DESC;
-- Insight: Flags cities where the delivery promise is being broken —
-- direct driver of cancellations and poor ratings.


-- Q13. Delivery partner performance comparison
SELECT
    Delivery_Partner,
    COUNT(*) AS total_orders,
    ROUND(AVG(Delivery_Time_Min), 2) AS avg_delivery_time,
    ROUND(AVG(Customer_Rating), 2)   AS avg_rating,
    ROUND(100.0 * COUNT(*) FILTER (WHERE Order_Status = 'Cancelled') / COUNT(*), 2) AS cancellation_rate_pct
FROM blinkit_orders
GROUP BY Delivery_Partner
ORDER BY avg_delivery_time DESC;
-- Insight: Surfaces underperforming delivery partners for retraining or
-- contract renegotiation.


-- Q14. Cancellation rate overall and by city
SELECT
    City,
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (WHERE Order_Status = 'Cancelled') AS cancelled_orders,
    ROUND(100.0 * COUNT(*) FILTER (WHERE Order_Status = 'Cancelled') / COUNT(*), 2) AS cancellation_rate_pct
FROM blinkit_orders
GROUP BY City
ORDER BY cancellation_rate_pct DESC;
-- Insight: Directly quantifies the core business problem by geography,
-- so operations can target fixes where they matter most.


-- Q15. Relationship between delivery time bucket and cancellation rate
SELECT
    CASE
        WHEN Delivery_Time_Min <= 10 THEN '0-10 min'
        WHEN Delivery_Time_Min <= 20 THEN '11-20 min'
        WHEN Delivery_Time_Min <= 30 THEN '21-30 min'
        ELSE '30+ min'
    END AS delivery_bucket,
    COUNT(*) AS total_orders,
    ROUND(100.0 * COUNT(*) FILTER (WHERE Order_Status = 'Cancelled') / COUNT(*), 2) AS cancellation_rate_pct,
    ROUND(AVG(Customer_Rating), 2) AS avg_rating
FROM blinkit_orders
GROUP BY 1
ORDER BY 1;
-- Insight: Proves (or disproves) that delivery delay is a root cause of
-- cancellations — the single most important insight for the project's story.


-- Q16. Store-level performance ranking
SELECT
    Store_ID,
    City,
    COUNT(*) AS orders,
    SUM(Final_Order_Value) AS revenue,
    ROUND(AVG(Delivery_Time_Min), 2) AS avg_delivery_time,
    DENSE_RANK() OVER (ORDER BY SUM(Final_Order_Value) DESC) AS revenue_rank
FROM blinkit_orders
WHERE Order_Status = 'Delivered'
GROUP BY Store_ID, City
ORDER BY revenue_rank;
-- Insight: Identifies top and bottom performing dark stores for
-- operational review or expansion planning.


-- Q17. Average customer rating trend by month
SELECT
    DATE_TRUNC('month', Order_Date) AS order_month,
    ROUND(AVG(Customer_Rating), 2) AS avg_rating
FROM blinkit_orders
WHERE Order_Status = 'Delivered'
GROUP BY 1
ORDER BY 1;
-- Insight: Ratings are a leading indicator of churn — a declining trend
-- should trigger investigation before revenue actually drops.


-- =========================================================================
-- SECTION 4: DISCOUNTS, COUPONS & PROFITABILITY
-- =========================================================================

-- Q18. Discount impact on order value and profit
SELECT
    Coupon_Used,
    COUNT(*) AS orders,
    ROUND(AVG(Final_Order_Value), 2) AS avg_order_value,
    ROUND(AVG(Profit), 2) AS avg_profit
FROM blinkit_orders
WHERE Order_Status = 'Delivered'
GROUP BY Coupon_Used;
-- Insight: Checks whether coupons are driving genuinely larger baskets or
-- just eating into margin without a volume payoff.


-- Q19. Profitability by product category
SELECT
    Product_Category,
    SUM(Profit)                         AS total_profit,
    ROUND(AVG(Profit), 2)               AS avg_profit_per_order,
    ROUND(100.0 * SUM(Profit) / NULLIF(SUM(Final_Order_Value), 0), 2) AS profit_margin_pct
FROM blinkit_orders
WHERE Order_Status = 'Delivered'
GROUP BY Product_Category
ORDER BY total_profit DESC;
-- Insight: Distinguishes "high revenue" categories from "high margin"
-- categories — sometimes they're not the same, which changes promo strategy.


-- Q20. Payment method distribution and average value
SELECT
    Payment_Method,
    COUNT(*) AS orders,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS order_share_pct,
    ROUND(AVG(Final_Order_Value), 2) AS avg_order_value
FROM blinkit_orders
WHERE Order_Status = 'Delivered'
GROUP BY Payment_Method
ORDER BY orders DESC;
-- Insight: COD-heavy segments often correlate with higher cancellation
-- risk — useful for targeting prepaid-adoption campaigns.


-- Q21. Running total of daily revenue (cumulative) using window function
SELECT
    Order_Date,
    SUM(Final_Order_Value) AS daily_revenue,
    SUM(SUM(Final_Order_Value)) OVER (ORDER BY Order_Date) AS cumulative_revenue
FROM blinkit_orders
WHERE Order_Status = 'Delivered'
GROUP BY Order_Date
ORDER BY Order_Date;
-- Insight: Useful for tracking progress against a quarterly/annual revenue target.


-- Q22. Top 3 products per category by revenue (ranking within group)
WITH ranked AS (
    SELECT
        Product_Category,
        Product_Name,
        SUM(Final_Order_Value) AS revenue,
        ROW_NUMBER() OVER (PARTITION BY Product_Category ORDER BY SUM(Final_Order_Value) DESC) AS rn
    FROM blinkit_orders
    WHERE Order_Status = 'Delivered'
    GROUP BY Product_Category, Product_Name
)
SELECT * FROM ranked WHERE rn <= 3
ORDER BY Product_Category, rn;
-- Insight: Gives a category manager a focused "hero SKU" list rather than
-- a flat top-10 across the whole catalogue.


-- =========================================================================
-- SECTION 5: MARKETING & PLATFORM ANALYSIS
-- =========================================================================

-- Q23. Revenue and order share by marketing channel
SELECT
    Marketing_Channel,
    COUNT(*) AS orders,
    SUM(Final_Order_Value) AS revenue,
    ROUND(AVG(Final_Order_Value), 2) AS avg_order_value
FROM blinkit_orders
WHERE Order_Status = 'Delivered'
GROUP BY Marketing_Channel
ORDER BY revenue DESC;
-- Insight: Helps reallocate acquisition budget toward channels producing
-- higher-value orders, not just more orders.


-- Q24. Device/platform split of orders
SELECT
    Device_Type,
    Platform,
    COUNT(*) AS orders,
    ROUND(AVG(Session_Duration_Min), 2) AS avg_session_duration
FROM blinkit_orders
GROUP BY Device_Type, Platform
ORDER BY orders DESC;
-- Insight: If Web/iOS underperform, it signals where product/UX
-- investment could unlock more orders.


-- Q25. City-wise performance summary (comprehensive)
SELECT
    City,
    COUNT(*) AS total_orders,
    SUM(Final_Order_Value) AS revenue,
    ROUND(AVG(Delivery_Time_Min), 2) AS avg_delivery_time,
    ROUND(100.0 * COUNT(*) FILTER (WHERE Order_Status = 'Cancelled') / COUNT(*), 2) AS cancellation_rate_pct,
    ROUND(AVG(Customer_Rating), 2) AS avg_rating
FROM blinkit_orders
GROUP BY City
ORDER BY revenue DESC;
-- Insight: One-stop city scorecard for regional leadership reviews.


-- Q26. Cancellation rate trend by month (CTE + window function)
WITH monthly_status AS (
    SELECT
        DATE_TRUNC('month', Order_Date) AS order_month,
        COUNT(*) AS total_orders,
        COUNT(*) FILTER (WHERE Order_Status = 'Cancelled') AS cancelled
    FROM blinkit_orders
    GROUP BY 1
)
SELECT
    order_month,
    ROUND(100.0 * cancelled / total_orders, 2) AS cancellation_rate_pct,
    ROUND(
        100.0 * cancelled / total_orders
        - LAG(100.0 * cancelled / total_orders) OVER (ORDER BY order_month), 2
    ) AS change_vs_prev_month
FROM monthly_status
ORDER BY order_month;
-- Insight: Shows whether the cancellation problem is improving or
-- worsening over time — critical for measuring if fixes are working.


-- Q27. High-value "at risk" customers: high spend but below-average rating given
WITH customer_stats AS (
    SELECT
        Customer_ID,
        SUM(Final_Order_Value) AS total_spend,
        AVG(Customer_Rating)   AS avg_rating_given
    FROM blinkit_orders
    WHERE Order_Status = 'Delivered'
    GROUP BY Customer_ID
)
SELECT *
FROM customer_stats
WHERE total_spend > (SELECT AVG(total_spend) FROM customer_stats)
  AND avg_rating_given < 3.5
ORDER BY total_spend DESC;
-- Insight: These are high-value customers actively signalling
-- dissatisfaction — the highest-priority churn-prevention list.


-- Q28. Order value distribution using NTILE (quartiles)
SELECT
    Order_ID,
    Final_Order_Value,
    NTILE(4) OVER (ORDER BY Final_Order_Value) AS value_quartile
FROM blinkit_orders
WHERE Order_Status = 'Delivered';
-- Insight: Basis for basket-size-based promotions (e.g. targeting Q1
-- customers with "spend more, save more" offers).


-- Q29. Average order value by day-of-week
SELECT
    TO_CHAR(Order_Date, 'Day') AS day_of_week,
    COUNT(*) AS orders,
    ROUND(AVG(Final_Order_Value), 2) AS avg_order_value
FROM blinkit_orders
WHERE Order_Status = 'Delivered'
GROUP BY 1, EXTRACT(DOW FROM Order_Date)
ORDER BY EXTRACT(DOW FROM Order_Date);
-- Insight: Informs staffing and inventory pre-positioning ahead of
-- consistently higher-demand days.


-- Q30. Overall business health scorecard (single summary query)
SELECT
    COUNT(*)                                                              AS total_orders,
    COUNT(*) FILTER (WHERE Order_Status = 'Delivered')                    AS delivered_orders,
    ROUND(100.0 * COUNT(*) FILTER (WHERE Order_Status = 'Cancelled') / COUNT(*), 2) AS cancellation_rate_pct,
    SUM(Final_Order_Value) FILTER (WHERE Order_Status = 'Delivered')      AS total_revenue,
    ROUND(AVG(Final_Order_Value) FILTER (WHERE Order_Status = 'Delivered'), 2) AS avg_order_value,
    ROUND(AVG(Delivery_Time_Min), 2)                                      AS avg_delivery_time,
    ROUND(AVG(Customer_Rating), 2)                                        AS avg_rating
FROM blinkit_orders;
-- Insight: The single query behind the Power BI KPI card row — ties every
-- number in the dashboard back to one source of truth.
