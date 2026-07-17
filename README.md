# Blinkit Order Analytics: Reducing Cancellations & Improving Delivery Performance

A placement-ready, end-to-end data analytics project analyzing Blinkit-style
quick-commerce order data using **SQL**, **Python**, and **Power BI**.

## Project Overview
This project simulates the workflow of a Data Analyst / Growth Analyst at a
quick-commerce company: start from a business problem, explore the data,
answer it with SQL and Python, and package findings into a dashboard and a
set of actionable recommendations for management.

## 📊 Sample Visualization

### Delivery Time vs Cancellation Rate

This chart shows that longer delivery times are associated with a higher cancellation rate, highlighting the importance of efficient logistics and delivery optimization.

<p align="center">
  <img src="/images/06_delivery_time_vs_cancellation.png" alt="Delivery Time vs Cancellation" width="800">
</p>

## Business Problem
Blinkit-style quick-commerce depends on fast, reliable delivery to retain
customers. This project investigates **rising order cancellations and
inconsistent delivery performance**, and tests the hypothesis that delivery
delays — not price or product mix — are the primary driver. Solving this
matters because every cancelled order is lost revenue, a wasted delivery
trip, and a customer less likely to reorder.

## Dataset
A realistic synthetic dataset of **22,220 orders** (`data/blinkit_orders.csv`)
generated with seasonal demand patterns, missing values, duplicates, and
pricing/delivery-time outliers — mirroring what a real operational export
looks like. Columns include order, customer, product, pricing, delivery,
payment, rating, and marketing-channel fields (28 columns total).

## Tools Used
- **SQL** — PostgreSQL-style queries (CTEs, window functions, ranking)
- **Python** — Pandas, NumPy, Matplotlib, Seaborn
- **Power BI** — KPI cards, charts, slicers
- **Excel/CSV** — source data format

## Analysis Process
1. **Data Generation** (`generate_data.py`) — realistic synthetic order data.
2. **SQL Analysis** (`sql/blinkit_analysis_queries.sql`) — 30 queries across
   revenue, customer segmentation, delivery performance, and profitability,
   each with a written business insight.
3. **Python EDA** (`notebooks/eda_analysis.py` / `.ipynb`) — cleaning,
   missing-value treatment, IQR-based outlier handling, feature
   engineering, and 15 visualizations (`images/`).
4. **Power BI Dashboard** (`dashboard/powerbi_dashboard_guide.md`) — build
   guide with DAX measures and layout for a single-page KPI dashboard.

## Dashboard
A single-page dashboard with:
- **KPI cards:** Total Revenue, Total Orders, Avg Order Value, Profit, Avg
  Delivery Time, Cancellation Rate
- **Charts:** Monthly Revenue, Category Sales, City-wise Sales, Customer
  Type Distribution, Top Products, Delivery Time vs Cancellation Rate
- **Slicers:** Date, City, Category, Customer Type

See `dashboard/powerbi_dashboard_guide.md` for the full build spec (DAX
measures + layout) to recreate the `.pbix` in Power BI Desktop.

## Key Insights
See `business_insights.md` for the full list of 20 insights. Headline
finding: orders that take over 30 minutes to deliver cancel at roughly
double the rate of orders delivered within 10 minutes, and this pattern
holds consistently across delivery-time buckets — strong evidence that
delivery speed, not pricing, is the primary lever behind cancellations.

## Results
- Analyzed 22,000+ orders across 8 cities and 10 product categories
- Identified the delivery-time threshold most strongly associated with cancellations
- Quantified repeat purchase rate and isolated a high-value "at risk" customer segment
- Delivered 15 practical recommendations in `recommendations.md`

## Installation
```bash
git clone <repo-url>
cd Blinkit-Analysis
pip install -r requirements.txt

# Regenerate the dataset (optional — one is already included in data/)
python generate_data.py

# Run the EDA and generate charts
cd notebooks
python eda_analysis.py
# or open eda_analysis.ipynb in Jupyter
```
For SQL: load `data/blinkit_orders_cleaned.csv` into a table named
`blinkit_orders` in PostgreSQL/MySQL, then run
`sql/blinkit_analysis_queries.sql`.

## Future Improvements
- Add a proper RFM (Recency, Frequency, Monetary) customer segmentation
- Statistical significance testing on the delivery-time/cancellation relationship
- Cohort retention analysis by signup month
- Automate the Python → Power BI refresh with a scheduled pipeline

## Project Structure
```
Blinkit-Analysis/
├── data/
│   ├── blinkit_orders.csv
│   └── blinkit_orders_cleaned.csv
├── sql/
│   └── blinkit_analysis_queries.sql
├── notebooks/
│   ├── eda_analysis.py
│   └── eda_analysis.ipynb
├── dashboard/
│   └── powerbi_dashboard_guide.md
├── images/
│   └── (15 chart PNGs)
├── business_insights.md
├── recommendations.md
├── generate_data.py
├── requirements.txt
└── README.md
```
