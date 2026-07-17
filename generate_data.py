"""
generate_data.py
-----------------
Generates a realistic synthetic Blinkit order-level dataset for the
"Reducing Order Cancellations & Improving Delivery Performance" analytics
project. Includes intentional data-quality issues (missing values,
duplicates, outliers) and seasonal/time-of-day patterns, as a real
quick-commerce export would.

Run: python generate_data.py
Output: data/blinkit_orders.csv
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

N_ROWS = 22000

# ---------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------
cities = ["Delhi", "Mumbai", "Bengaluru", "Pune", "Hyderabad", "Chennai", "Kolkata", "Ahmedabad"]
city_weights = [0.20, 0.18, 0.15, 0.10, 0.10, 0.09, 0.10, 0.08]

areas_by_city = {
    "Delhi": ["Dwarka", "Rohini", "Saket", "Karol Bagh", "Vasant Kunj"],
    "Mumbai": ["Andheri", "Bandra", "Powai", "Malad", "Thane"],
    "Bengaluru": ["Koramangala", "Whitefield", "Indiranagar", "HSR Layout", "Jayanagar"],
    "Pune": ["Kothrud", "Hinjewadi", "Viman Nagar", "Baner", "Wakad"],
    "Hyderabad": ["Gachibowli", "Madhapur", "Kukatpally", "Banjara Hills", "Secunderabad"],
    "Chennai": ["Adyar", "T Nagar", "Velachery", "Anna Nagar", "OMR"],
    "Kolkata": ["Salt Lake", "Park Street", "Behala", "Howrah", "Garia"],
    "Ahmedabad": ["Navrangpura", "Satellite", "Bopal", "Maninagar", "Vastrapur"],
}

categories = {
    "Fruits & Vegetables": ["Banana", "Onion", "Tomato", "Apple", "Potato", "Spinach"],
    "Dairy & Breakfast": ["Milk 1L", "Curd 400g", "Bread", "Eggs 6pc", "Paneer 200g"],
    "Snacks": ["Lays Chips", "Kurkure", "Biscuits Pack", "Namkeen 200g", "Chocolate Bar"],
    "Beverages": ["Coca-Cola 750ml", "Mango Juice 1L", "Mineral Water 1L", "Coffee Powder", "Tea Bags"],
    "Personal Care": ["Shampoo 200ml", "Toothpaste", "Soap Bar", "Face Wash", "Hand Sanitizer"],
    "Home Care": ["Dish Soap", "Detergent 1kg", "Toilet Cleaner", "Floor Cleaner", "Room Freshener"],
    "Staples": ["Rice 5kg", "Atta 5kg", "Sugar 1kg", "Cooking Oil 1L", "Salt 1kg"],
    "Baby Care": ["Diapers Pack", "Baby Wipes", "Baby Lotion", "Baby Food"],
    "Pet Care": ["Dog Food 1kg", "Cat Litter", "Pet Shampoo"],
    "Electronics Essentials": ["Batteries AA", "USB Cable", "Earphones"],
}

category_price_range = {
    "Fruits & Vegetables": (10, 80),
    "Dairy & Breakfast": (25, 150),
    "Snacks": (10, 120),
    "Beverages": (20, 150),
    "Personal Care": (40, 300),
    "Home Care": (50, 250),
    "Staples": (60, 600),
    "Baby Care": (100, 700),
    "Pet Care": (150, 800),
    "Electronics Essentials": (99, 999),
}

payment_methods = ["UPI", "Credit/Debit Card", "Cash on Delivery", "Wallet", "Net Banking"]
payment_weights = [0.45, 0.20, 0.15, 0.15, 0.05]

delivery_partners = ["Partner A", "Partner B", "Partner C", "Partner D", "Partner E"]
customer_types = ["New", "Returning", "Loyal"]
device_types = ["Android", "iOS"]
platforms = ["App", "Web"]
marketing_channels = ["Organic", "Paid Ads", "Referral", "Push Notification", "Social Media", "Email"]
app_versions = ["8.4.1", "8.5.0", "8.6.2", "8.7.0", "8.8.1"]
order_statuses = ["Delivered", "Cancelled", "Returned"]

start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)
date_range_days = (end_date - start_date).days

# Seasonal weight: higher orders around festive months (Oct-Nov) and month-start salary days
def seasonal_weight(date):
    weight = 1.0
    if date.month in (10, 11):          # festive season boost
        weight *= 1.6
    if date.month == 12:                # year-end mild boost
        weight *= 1.2
    if date.day <= 5:                   # salary-day boost
        weight *= 1.3
    if date.weekday() in (5, 6):        # weekend boost
        weight *= 1.25
    return weight

day_offsets = np.arange(date_range_days + 1)
dates = [start_date + timedelta(days=int(d)) for d in day_offsets]
weights = np.array([seasonal_weight(d) for d in dates])
weights = weights / weights.sum()

order_dates = np.random.choice(dates, size=N_ROWS, p=weights)

# ---------------------------------------------------------------------
# Build rows
# ---------------------------------------------------------------------
rows = []
n_customers = 9000
customer_ids = [f"CUST{100000+i}" for i in range(n_customers)]
# give some customers repeat-purchase propensity (power law)
customer_probs = np.random.pareto(2.0, n_customers) + 0.1
customer_probs = customer_probs / customer_probs.sum()

store_ids = {city: [f"STR-{city[:3].upper()}-{i}" for i in range(1, 7)] for city in cities}

for i in range(N_ROWS):
    order_date = pd.Timestamp(order_dates[i])
    city = np.random.choice(cities, p=city_weights)
    area = random.choice(areas_by_city[city])
    store_id = random.choice(store_ids[city])
    category = random.choice(list(categories.keys()))
    product = random.choice(categories[category])
    qty = np.random.choice([1, 2, 3, 4, 5], p=[0.45, 0.25, 0.15, 0.10, 0.05])

    low, high = category_price_range[category]
    unit_price = round(np.random.uniform(low, high), 2)

    # occasional pricing outliers (data entry errors)
    if random.random() < 0.003:
        unit_price = unit_price * random.choice([10, 0.01])

    selling_price = round(unit_price * qty, 2)

    discount_pct = np.random.choice([0, 5, 10, 15, 20, 25], p=[0.35, 0.2, 0.2, 0.15, 0.07, 0.03])
    discount = round(selling_price * discount_pct / 100, 2)

    cart_value = round(selling_price - discount, 2)
    delivery_fee = 0 if cart_value > 199 else round(np.random.choice([15, 20, 25, 30]), 2)

    final_order_value = round(cart_value + delivery_fee, 2)

    # cost estimate for profit calc (55-75% of selling price depending on category)
    cost_ratio = np.random.uniform(0.55, 0.75)
    cost = round(selling_price * cost_ratio, 2)
    profit = round(final_order_value - cost - discount, 2)

    # delivery time: base 10 min promise, with delays during festive/weekend/rain-like noise
    base_time = np.random.normal(14, 4)
    if order_date.month in (10, 11):
        base_time += np.random.normal(4, 2)
    if order_date.weekday() in (5, 6):
        base_time += np.random.normal(2, 1)
    delivery_time = max(5, round(base_time, 1))
    # outliers - severe delays
    if random.random() < 0.01:
        delivery_time = round(delivery_time + np.random.uniform(30, 90), 1)

    order_hour = int(np.clip(np.random.normal(14, 5), 0, 23))
    order_time = f"{order_hour:02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"

    # order status - cancellations more likely with long delivery time
    cancel_prob = 0.06 + (0.002 * max(0, delivery_time - 20))
    return_prob = 0.02
    status_roll = random.random()
    if status_roll < cancel_prob:
        order_status = "Cancelled"
    elif status_roll < cancel_prob + return_prob:
        order_status = "Returned"
    else:
        order_status = "Delivered"

    customer_idx = np.random.choice(n_customers, p=customer_probs)
    customer_id = customer_ids[customer_idx]
    customer_type = np.random.choice(customer_types, p=[0.35, 0.45, 0.20])

    rating = np.nan
    if order_status == "Delivered":
        rating_base = 4.3 - (0.03 * max(0, delivery_time - 15))
        rating = round(np.clip(np.random.normal(rating_base, 0.6), 1, 5), 0)

    coupon_used = np.random.choice(["Yes", "No"], p=[0.3, 0.7]) if discount_pct > 0 else "No"

    row = {
        "Order_ID": f"ORD{200000+i}",
        "Customer_ID": customer_id,
        "City": city,
        "Area": area,
        "Store_ID": store_id,
        "Product_Category": category,
        "Product_Name": product,
        "Quantity": qty,
        "Selling_Price": selling_price,
        "Discount": discount,
        "Delivery_Fee": delivery_fee,
        "Delivery_Time_Min": delivery_time,
        "Order_Time": order_time,
        "Order_Date": order_date.strftime("%Y-%m-%d"),
        "Payment_Method": np.random.choice(payment_methods, p=payment_weights),
        "Delivery_Partner": random.choice(delivery_partners),
        "Order_Status": order_status,
        "Customer_Rating": rating,
        "Customer_Type": customer_type,
        "Coupon_Used": coupon_used,
        "App_Version": random.choice(app_versions),
        "Device_Type": np.random.choice(device_types, p=[0.75, 0.25]),
        "Platform": np.random.choice(platforms, p=[0.9, 0.1]),
        "Session_Duration_Min": round(max(0.5, np.random.normal(4, 2)), 1),
        "Cart_Value": cart_value,
        "Final_Order_Value": final_order_value,
        "Profit": profit,
        "Marketing_Channel": np.random.choice(marketing_channels, p=[0.35, 0.2, 0.15, 0.15, 0.1, 0.05]),
    }
    rows.append(row)

df = pd.DataFrame(rows)

# ---------------------------------------------------------------------
# Inject realistic data-quality issues
# ---------------------------------------------------------------------
# Missing values
for col, frac in [("Customer_Rating", 0.0), ("Delivery_Partner", 0.01),
                   ("Coupon_Used", 0.02), ("Session_Duration_Min", 0.015),
                   ("Area", 0.01), ("Discount", 0.005)]:
    n_missing = int(len(df) * frac)
    if n_missing > 0:
        idx = np.random.choice(df.index, n_missing, replace=False)
        df.loc[idx, col] = np.nan

# Duplicates (~1%)
dup_rows = df.sample(frac=0.01, random_state=1)
df = pd.concat([df, dup_rows], ignore_index=True)

# Shuffle
df = df.sample(frac=1, random_state=7).reset_index(drop=True)

df.to_csv("/home/claude/Blinkit-Analysis/data/blinkit_orders.csv", index=False)
print("Saved:", df.shape)
print(df.head())
