"""
eda_analysis.py
----------------
End-to-end EDA for the Blinkit order dataset: cleaning, feature engineering,
and visualization. Designed to be readable and explainable in an interview,
not "clever" — every step maps to a specific business question.

Run: python eda_analysis.py
Outputs: PNG charts saved to ../images/
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 110

IMG_DIR = "../images"
DATA_PATH = "../data/blinkit_orders.csv"

# -------------------------------------------------------------------------
# 1. LOAD & CLEAN
# -------------------------------------------------------------------------
df = pd.read_csv(DATA_PATH)
print("Raw shape:", df.shape)

# Drop exact duplicate rows
before = len(df)
df = df.drop_duplicates()
print(f"Removed {before - len(df)} duplicate rows")

# Parse dates
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df["Order_Month"] = df["Order_Date"].dt.to_period("M").astype(str)
df["Order_Weekday"] = df["Order_Date"].dt.day_name()

# Missing value treatment
# Customer_Rating: legitimately missing for non-delivered orders -> leave as NaN
# Delivery_Partner / Coupon_Used / Area: impute with mode (categorical)
for col in ["Delivery_Partner", "Coupon_Used", "Area"]:
    mode_val = df[col].mode()[0]
    df[col] = df[col].fillna(mode_val)

# Discount: impute missing with 0 (no discount recorded)
df["Discount"] = df["Discount"].fillna(0)

# Session_Duration_Min: impute with median
df["Session_Duration_Min"] = df["Session_Duration_Min"].fillna(df["Session_Duration_Min"].median())

print("\nMissing values after treatment:\n", df.isnull().sum()[df.isnull().sum() > 0])

# -------------------------------------------------------------------------
# 2. OUTLIER DETECTION (IQR method on key numeric columns)
# -------------------------------------------------------------------------
def iqr_bounds(series):
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr

for col in ["Final_Order_Value", "Delivery_Time_Min"]:
    low, high = iqr_bounds(df[col])
    n_outliers = ((df[col] < low) | (df[col] > high)).sum()
    print(f"{col}: {n_outliers} outliers outside [{low:.1f}, {high:.1f}]")

# Cap extreme pricing errors (e.g. 10x/0.01x glitches) rather than drop rows,
# to preserve sample size while neutralizing their skew
low, high = iqr_bounds(df["Final_Order_Value"])
df["Final_Order_Value_Capped"] = df["Final_Order_Value"].clip(lower=max(0, low), upper=high * 1.5)

# -------------------------------------------------------------------------
# 3. FEATURE ENGINEERING
# -------------------------------------------------------------------------
df["Delivery_Time_Bucket"] = pd.cut(
    df["Delivery_Time_Min"],
    bins=[0, 10, 20, 30, np.inf],
    labels=["0-10 min", "11-20 min", "21-30 min", "30+ min"]
)
df["Is_Cancelled"] = (df["Order_Status"] == "Cancelled").astype(int)
df["Is_Delivered"] = (df["Order_Status"] == "Delivered").astype(int)
df["Order_Hour"] = df["Order_Time"].str.split(":").str[0].astype(int)

delivered = df[df["Order_Status"] == "Delivered"].copy()

# -------------------------------------------------------------------------
# 4. VISUALIZATIONS
# -------------------------------------------------------------------------

# 4.1 Monthly revenue trend
monthly_rev = delivered.groupby("Order_Month")["Final_Order_Value"].sum().reset_index()
plt.figure(figsize=(10, 5))
sns.lineplot(data=monthly_rev, x="Order_Month", y="Final_Order_Value", marker="o")
plt.title("Monthly Revenue Trend (2024)")
plt.xlabel("Month"); plt.ylabel("Revenue (₹)")
plt.xticks(rotation=45)
plt.tight_layout(); plt.savefig(f"{IMG_DIR}/01_monthly_revenue_trend.png"); plt.close()

# 4.2 Revenue by category
cat_rev = delivered.groupby("Product_Category")["Final_Order_Value"].sum().sort_values()
plt.figure(figsize=(9, 6))
cat_rev.plot(kind="barh", color="#0c831f")
plt.title("Revenue by Product Category")
plt.xlabel("Revenue (₹)")
plt.tight_layout(); plt.savefig(f"{IMG_DIR}/02_revenue_by_category.png"); plt.close()

# 4.3 Orders by city
plt.figure(figsize=(9, 5))
sns.countplot(data=df, y="City", order=df["City"].value_counts().index, color="#f8cb46")
plt.title("Order Volume by City")
plt.xlabel("Orders"); plt.ylabel("City")
plt.tight_layout(); plt.savefig(f"{IMG_DIR}/03_orders_by_city.png"); plt.close()

# 4.4 Cancellation rate by city
cancel_city = df.groupby("City")["Is_Cancelled"].mean().sort_values(ascending=False) * 100
plt.figure(figsize=(9, 5))
cancel_city.plot(kind="bar", color="#e94b3c")
plt.title("Cancellation Rate by City")
plt.ylabel("Cancellation Rate (%)")
plt.xticks(rotation=45)
plt.tight_layout(); plt.savefig(f"{IMG_DIR}/04_cancellation_rate_by_city.png"); plt.close()

# 4.5 Delivery time distribution
plt.figure(figsize=(8, 5))
sns.histplot(df["Delivery_Time_Min"], bins=40, kde=True, color="#0c831f")
plt.title("Delivery Time Distribution")
plt.xlabel("Delivery Time (minutes)")
plt.tight_layout(); plt.savefig(f"{IMG_DIR}/05_delivery_time_distribution.png"); plt.close()

# 4.6 Delivery time bucket vs cancellation rate (key business insight)
bucket_cancel = df.groupby("Delivery_Time_Bucket", observed=True)["Is_Cancelled"].mean() * 100
plt.figure(figsize=(8, 5))
bucket_cancel.plot(kind="bar", color="#e94b3c")
plt.title("Cancellation Rate by Delivery Time Bucket")
plt.ylabel("Cancellation Rate (%)"); plt.xlabel("Delivery Time Bucket")
plt.xticks(rotation=0)
plt.tight_layout(); plt.savefig(f"{IMG_DIR}/06_delivery_time_vs_cancellation.png"); plt.close()

# 4.7 Customer type distribution
plt.figure(figsize=(6, 6))
df["Customer_Type"].value_counts().plot(
    kind="pie", autopct="%1.1f%%", colors=["#0c831f", "#f8cb46", "#e94b3c"]
)
plt.title("Customer Type Distribution")
plt.ylabel("")
plt.tight_layout(); plt.savefig(f"{IMG_DIR}/07_customer_type_distribution.png"); plt.close()

# 4.8 Top 10 products by units sold
top_products = delivered.groupby("Product_Name")["Quantity"].sum().sort_values(ascending=False).head(10)
plt.figure(figsize=(9, 6))
top_products.sort_values().plot(kind="barh", color="#0c831f")
plt.title("Top 10 Products by Units Sold")
plt.xlabel("Units Sold")
plt.tight_layout(); plt.savefig(f"{IMG_DIR}/08_top_10_products.png"); plt.close()

# 4.9 Average order value by day of week
dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
aov_dow = delivered.groupby("Order_Weekday")["Final_Order_Value"].mean().reindex(dow_order)
plt.figure(figsize=(9, 5))
aov_dow.plot(kind="bar", color="#f8cb46")
plt.title("Average Order Value by Day of Week")
plt.ylabel("Avg Order Value (₹)")
plt.xticks(rotation=45)
plt.tight_layout(); plt.savefig(f"{IMG_DIR}/09_aov_by_weekday.png"); plt.close()

# 4.10 Order volume by hour of day
plt.figure(figsize=(9, 5))
sns.countplot(data=df, x="Order_Hour", color="#0c831f")
plt.title("Order Volume by Hour of Day")
plt.xlabel("Hour"); plt.ylabel("Orders")
plt.tight_layout(); plt.savefig(f"{IMG_DIR}/10_orders_by_hour.png"); plt.close()

# 4.11 Correlation heatmap of key numeric features
num_cols = ["Quantity", "Selling_Price", "Discount", "Delivery_Fee",
            "Delivery_Time_Min", "Session_Duration_Min", "Final_Order_Value", "Profit"]
plt.figure(figsize=(9, 7))
sns.heatmap(df[num_cols].corr(), annot=True, fmt=".2f", cmap="RdYlGn", center=0)
plt.title("Correlation Heatmap – Key Numeric Features")
plt.tight_layout(); plt.savefig(f"{IMG_DIR}/11_correlation_heatmap.png"); plt.close()

# 4.12 Profit margin by category
delivered["Margin_Pct"] = (delivered["Profit"] / delivered["Final_Order_Value"]) * 100
margin_cat = delivered.groupby("Product_Category")["Margin_Pct"].mean().sort_values()
plt.figure(figsize=(9, 6))
margin_cat.plot(kind="barh", color="#0c831f")
plt.title("Average Profit Margin (%) by Category")
plt.xlabel("Margin (%)")
plt.tight_layout(); plt.savefig(f"{IMG_DIR}/12_profit_margin_by_category.png"); plt.close()

# 4.13 Rating distribution
plt.figure(figsize=(7, 5))
sns.countplot(data=delivered, x="Customer_Rating", color="#f8cb46")
plt.title("Customer Rating Distribution (Delivered Orders)")
plt.xlabel("Rating"); plt.ylabel("Orders")
plt.tight_layout(); plt.savefig(f"{IMG_DIR}/13_rating_distribution.png"); plt.close()

# 4.14 Marketing channel: orders vs avg order value
mkt = delivered.groupby("Marketing_Channel").agg(
    orders=("Order_ID", "count"), avg_value=("Final_Order_Value", "mean")
).sort_values("orders", ascending=False)
fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.bar(mkt.index, mkt["orders"], color="#0c831f")
ax1.set_ylabel("Orders", color="#0c831f")
ax1.set_xticklabels(mkt.index, rotation=30)
ax2 = ax1.twinx()
ax2.plot(mkt.index, mkt["avg_value"], color="#e94b3c", marker="o")
ax2.set_ylabel("Avg Order Value (₹)", color="#e94b3c")
plt.title("Marketing Channel: Volume vs Average Order Value")
plt.tight_layout(); plt.savefig(f"{IMG_DIR}/14_marketing_channel_performance.png"); plt.close()

# 4.15 Delivery time trend by month (seasonality of ops performance)
delivery_trend = df.groupby("Order_Month")["Delivery_Time_Min"].mean().reset_index()
plt.figure(figsize=(10, 5))
sns.lineplot(data=delivery_trend, x="Order_Month", y="Delivery_Time_Min", marker="o", color="#e94b3c")
plt.title("Average Delivery Time by Month")
plt.xlabel("Month"); plt.ylabel("Avg Delivery Time (min)")
plt.xticks(rotation=45)
plt.tight_layout(); plt.savefig(f"{IMG_DIR}/15_delivery_time_trend.png"); plt.close()

print("\nAll 15 charts saved to", IMG_DIR)

# -------------------------------------------------------------------------
# 5. SAVE CLEANED DATASET
# -------------------------------------------------------------------------
df.to_csv("../data/blinkit_orders_cleaned.csv", index=False)
print("Cleaned dataset saved to ../data/blinkit_orders_cleaned.csv")
