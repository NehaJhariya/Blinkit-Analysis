# Power BI Dashboard – Build Guide

This document specifies exactly how to build the Blinkit dashboard in Power BI
Desktop from `blinkit_orders_cleaned.csv`. It covers data load, DAX measures,
page layout, and the purpose of every visual — everything needed to
rebuild and explain the `.pbix` in an interview.

## 1. Data Load
1. Get Data → Text/CSV → select `data/blinkit_orders_cleaned.csv`.
2. In Power Query, confirm data types: `Order_Date` = Date, all money fields =
   Decimal Number, `Delivery_Time_Min` = Decimal Number.
3. Create a `Date` dimension table (Modeling → New Table) and mark it as the
   official Date Table, then relate it to `Order_Date` (1-to-many).

## 2. DAX Measures
```DAX
Total Revenue = SUM(blinkit_orders[Final_Order_Value])

Total Orders = COUNTROWS(blinkit_orders)

Avg Order Value = DIVIDE([Total Revenue], [Total Orders])

Total Profit = SUM(blinkit_orders[Profit])

Avg Delivery Time = AVERAGE(blinkit_orders[Delivery_Time_Min])

Cancelled Orders = CALCULATE([Total Orders], blinkit_orders[Order_Status] = "Cancelled")

Cancellation Rate = DIVIDE([Cancelled Orders], [Total Orders])

Repeat Customers =
CALCULATE(
    DISTINCTCOUNT(blinkit_orders[Customer_ID]),
    FILTER(
        VALUES(blinkit_orders[Customer_ID]),
        CALCULATE(COUNTROWS(blinkit_orders)) > 1
    )
)

Profit Margin % = DIVIDE([Total Profit], [Total Revenue])
```

## 3. Page Layout (single page, KPI-first — kept simple on purpose)

**Row 1 — KPI Cards**
- Total Revenue | Total Orders | Avg Order Value | Total Profit | Avg Delivery Time | Cancellation Rate
- Purpose: gives leadership the full business health snapshot in five seconds.

**Row 2 — Trend & Category**
- *Monthly Revenue* (line chart, Order_Month on X) — shows growth/seasonality.
- *Category Sales* (bar chart, Product_Category by revenue) — shows which
  categories to protect or promote.

**Row 3 — Geography & Customers**
- *City-wise Sales* (map or bar chart) — shows where revenue and problems concentrate.
- *Customer Type Distribution* (donut: New/Returning/Loyal) — shows retention mix.

**Row 4 — Products & Delivery**
- *Top Products* (bar chart, top 10 by units sold) — inventory priority list.
- *Delivery Time Analysis* (bar chart: cancellation rate by delivery-time bucket)
  — the chart that visually proves the core business problem.

**Slicers panel (left side)**
- Date range slicer (Order_Date)
- City slicer
- Product_Category slicer
- Customer_Type slicer

## 4. Design Notes
- Use Blinkit's brand colors for consistency: green `#0C831F`, yellow `#F8CB46`,
  red `#E94B3C` for negative/alert metrics (e.g. cancellation rate).
- Keep the whole story on one page — a recruiter should understand the
  business problem and the evidence without clicking through tabs.
- Conditional formatting on the Cancellation Rate card (red if > 8%, else green)
  makes the "problem" visually obvious immediately.

## 5. Why this scope (not more)
Per the project's fresher/placement scope, this is intentionally a
single-page operational dashboard — not a multi-page enterprise BI suite.
It's built to be fully explainable end-to-end in a 5-minute interview walkthrough.
