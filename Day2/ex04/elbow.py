import os
import socket
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from sklearn.cluster import KMeans

# --- Display detection ---
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

# --- Build per-user features ---
user_features = (
    df.groupby("user_id")["event_price"]
      .agg(purchase_count="count", total_spent="sum", avg_basket="mean")
      .reset_index()
)

X = user_features[["purchase_count", "total_spent", "avg_basket"]]

# --- Elbow Method ---
inertias = []
k_values = range(1, 11)

for k in k_values:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto")
    kmeans.fit(X)
    inertias.append(kmeans.inertia_)

# --- Plot ---
plt.figure(figsize=(7, 5))
plt.plot(k_values, inertias, marker="o", color="dodgerblue")
plt.title("Elbow Method – Optimal Number of Clusters")
plt.xlabel("Number of Clusters (k)")
plt.ylabel("Inertia (Sum of Squared Distances)")
plt.xticks(k_values)
plt.grid(True)
plt.tight_layout()
plt.savefig("elbow_method.png", dpi=120)

if HEADLESS:
    print("\n[✔] Headless mode → Saved elbow chart:")
else:
    print("\n[INFO] Display available → Showing elbow chart.")
    plt.show()

print("   ", os.path.abspath("elbow_method.png"))
