import os
import socket
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

# detect if a real display exists
def has_display() -> bool:
    d = os.environ.get("DISPLAY")
    if not d:
        return False
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(d)
        s.close()
        return True
    except Exception:
        return False

# Backend setup (headless mode for WSL)
if not has_display():
    matplotlib.use("Agg")
    HEADLESS = True
else:
    HEADLESS = False

# Connect to PostgreSQL via SQLAlchemy
engine = create_engine("postgresql+psycopg2://gtskitis:mysecretpassword@localhost/piscineds")

# Load only purchase data from customers
query = """
    SELECT *
    FROM customers
    WHERE lower(event_type) = 'purchase';
"""
df = pd.read_sql_query(query, engine)
if df.empty:
    raise SystemExit("No purchase data found in customers table.")

# Keep data between Oct 2022 → Feb 2023
df["event_time"] = pd.to_datetime(df["event_time"])
mask = (df["event_time"] >= "2022-10-01") & (df["event_time"] < "2023-03-01")
df = df.loc[mask]

# Create columns for analysis
df["month"] = df["event_time"].dt.to_period("M")

# Chart 1 – Total revenue per month
monthly_revenue = df.groupby("month")["event_price"].sum().reset_index()

plt.figure(figsize=(8, 5))
plt.plot(monthly_revenue["month"].astype(str), monthly_revenue["event_price"],
         marker="o", color="dodgerblue")
plt.title("Total Revenue per Month (Oct 2022 – Feb 2023)")
plt.xlabel("Month")
plt.ylabel("Revenue (Altairian $)")
plt.tight_layout()
plt.savefig("chart_revenue.png", dpi=120)

# Chart 2 – Average basket event_price per user
basket = df.groupby("user_id")["event_price"].mean().reset_index()

plt.figure(figsize=(6, 4))
plt.hist(basket["event_price"], bins=50, color="skyblue", edgecolor="black")
plt.title("Average Basket Price per User")
plt.xlabel("Price (Altairian $)")
plt.ylabel("User Count")
plt.tight_layout()
plt.savefig("chart_avg_basket.png", dpi=120)

# Chart 3 – Number of purchases per month
purchase_count = df.groupby("month")["event_type"].count().reset_index()

plt.figure(figsize=(8, 5))
plt.bar(purchase_count["month"].astype(str), purchase_count["event_type"],
        color="orange", edgecolor="black")
plt.title("Number of Purchases per Month")
plt.xlabel("Month")
plt.ylabel("Purchase Count")
plt.tight_layout()
plt.savefig("chart_purchases.png", dpi=120)

if HEADLESS:
    print("[✔] Headless mode → Saved charts:")
else:
    print("[INFO] Display available → Showing last chart.")
    plt.show()

for f in ["chart_revenue.png", "chart_avg_basket.png", "chart_purchases.png"]:
    print("   ", os.path.abspath(f))
