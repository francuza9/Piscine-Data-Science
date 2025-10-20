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

# --- Connect to your DB ---
engine = create_engine("postgresql+psycopg2://gtskitis:mysecretpassword@localhost/piscineds")

# --- Load purchase data ---
query = """
    SELECT *
    FROM customers
    WHERE lower(event_type) = 'purchase';
"""
df = pd.read_sql_query(query, engine)
if df.empty:
    raise SystemExit("No purchase data found in customers table.")

df["event_time"] = pd.to_datetime(df["event_time"])
mask = (df["event_time"] >= "2022-10-01") & (df["event_time"] < "2023-03-01")
df = df.loc[mask]

# --- Descriptive statistics ---
desc = df["event_price"].describe(percentiles=[0.25, 0.5, 0.75])
print("\n[📊] Summary statistics for purchase prices:\n", desc)

# --- 1. Boxplot for all purchase prices ---
plt.figure(figsize=(8, 2))
plt.boxplot(df["event_price"], vert=False, patch_artist=True,
            boxprops=dict(facecolor="lightblue", color="black"),
            medianprops=dict(color="red", linewidth=2))
plt.title("Boxplot – Item Prices (Purchases Only)")
plt.xlabel("Price (Altairian $)")
plt.tight_layout()
plt.savefig("boxplot_prices.png", dpi=120)

# --- 2. Boxplot for average basket per user ---
basket = df.groupby("user_id")["event_price"].mean().reset_index()

plt.figure(figsize=(8, 2))
plt.boxplot(basket["event_price"], vert=False, patch_artist=True,
            boxprops=dict(facecolor="lightgreen", color="black"),
            medianprops=dict(color="red", linewidth=2))
plt.title("Boxplot – Average Basket Price per User")
plt.xlabel("Average Price (Altairian $)")
plt.tight_layout()
plt.savefig("boxplot_avg_basket.png", dpi=120)

if HEADLESS:
    print("\n[✔] Headless mode → Saved boxplots:")
else:
    print("\n[INFO] Display available → Showing last boxplot.")
    plt.show()

for f in ["boxplot_prices.png", "boxplot_avg_basket.png"]:
    print("   ", os.path.abspath(f))
