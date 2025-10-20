import os
import socket
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

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

if not has_display():
    matplotlib.use("Agg")
    HEADLESS = True
else:
    HEADLESS = False

# --- Connect to PostgreSQL ---
engine = create_engine("postgresql+psycopg2://gtskitis:mysecretpassword@localhost/piscineds")

# --- Load only purchases ---
query = """
    SELECT *
    FROM customers
    WHERE lower(event_type) = 'purchase';
"""
df = pd.read_sql_query(query, engine)
if df.empty:
    raise SystemExit("No purchase data found in customers table.")

# --- Restrict to Oct 2022 → Feb 2023 ---
df["event_time"] = pd.to_datetime(df["event_time"])
mask = (df["event_time"] >= "2022-10-01") & (df["event_time"] < "2023-03-01")
df = df.loc[mask]

# --- Count purchases per user ---
user_counts = df.groupby("user_id")["event_price"].count().reset_index(name="purchase_count")

# --- Chart 1: Customers by purchase frequency (0–10–20–30–40) ---
plt.figure(figsize=(8, 5))
bins = range(0, 41, 10)  # exactly 0,10,20,30,40
plt.hist(user_counts["purchase_count"], bins=bins, color="skyblue", edgecolor="black")
plt.title("Number of Customers by Purchase Frequency")
plt.xlabel("Number of Purchases")
plt.ylabel("Customers")
plt.xticks(bins)
plt.xlim(0, 40)
plt.tight_layout()
plt.savefig("bar_purchase_frequency.png", dpi=120)

# --- Total spent per user ---
user_spent = df.groupby("user_id")["event_price"].sum().reset_index(name="total_spent")

# --- Chart 2: Total money spent by customers (0–50–100–150–200–250) ---
plt.figure(figsize=(8, 5))
bins_spent = range(0, 301, 50)
plt.hist(user_spent["total_spent"], bins=bins_spent, color="lightgreen", edgecolor="black")
plt.title("Total Altairian Dollars Spent by Customers")
plt.xlabel("Total Spent (Altairian $)")
plt.ylabel("Customers")
plt.xticks(range(0, 301, 50))
plt.xlim(0, 250)
plt.tight_layout()
plt.savefig("bar_total_spent.png", dpi=120)

# --- Output ---
if HEADLESS:
    print("\n[✔] Headless mode → Saved bar charts:")
else:
    print("\n[INFO] Display available → Showing last chart.")
    plt.show()

for f in ["bar_purchase_frequency.png", "bar_total_spent.png"]:
    print("   ", os.path.abspath(f))
