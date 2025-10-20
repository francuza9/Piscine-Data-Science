import os
import socket
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# ---------- display detection ----------
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

# ---------- DB ----------
engine = create_engine("postgresql+psycopg2://gtskitis:mysecretpassword@localhost/piscineds")

# ---------- data ----------
q = "SELECT * FROM customers WHERE lower(event_type)='purchase';"
df = pd.read_sql_query(q, engine)
if df.empty:
    raise SystemExit("No purchase data found in customers table.")

df["event_time"] = pd.to_datetime(df["event_time"])
mask = (df["event_time"] >= "2022-10-01") & (df["event_time"] < "2023-03-01")
df = df.loc[mask]

# ---------- RFM ----------
now = df["event_time"].max() + pd.Timedelta(days=1)
rfm = (
    df.groupby("user_id")
      .agg(
          recency=("event_time", lambda x: (now - x.max()).days / 30.0),
          frequency=("event_time", "count"),
          monetary=("event_price", "sum"),
      )
      .reset_index()
)

# ---------- clustering features (stabilize + scale) ----------
feat = rfm.copy()

# ensure no negative/NaN values
feat["frequency"] = feat["frequency"].clip(lower=0)
feat["monetary"] = feat["monetary"].clip(lower=0)

# avoid log of 0 or negative
feat["frequency_log"] = np.log1p(feat["frequency"])
feat["monetary_log"] = np.log1p(feat["monetary"])

X = feat[["recency", "frequency_log", "monetary_log"]].replace([np.inf, -np.inf], np.nan).dropna()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

k = 5
kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto")
rfm = rfm.loc[X.index]  # keep only clean rows
rfm["cluster"] = kmeans.fit_predict(X_scaled)


# =======================================================
# 1) Loyal -> New -> Inactive (COUNTS; correct order & top-to-bottom)
# =======================================================

# Compute quantile thresholds for balanced segmentation
q1 = rfm["recency"].quantile(1/3)
q2 = rfm["recency"].quantile(4/5)

# Define segments dynamically so counts look reasonable
rfm["segment"] = pd.cut(
    rfm["recency"],
    bins=[-np.inf, q1, q2, np.inf],
    labels=["Loyal customers", "New customers", "Inactive"],
)

order = ["Loyal customers", "New customers", "Inactive"]

segment_counts = (
    rfm["segment"]
      .value_counts()
      .reindex(order)
      .fillna(0)
      .astype(int)
)

plt.figure(figsize=(8, 4))
bars = plt.barh(order, segment_counts.values,
                color=["orange", "lightgreen", "lightblue"], edgecolor="black")
plt.title("Customer Segments (Counts)")
plt.xlabel("Customers (0 → 40000)")
plt.xlim(0, 40000)

# Loyal customers appear on top
plt.gca().invert_yaxis()

# annotate counts
for b, v in zip(bars, segment_counts.values):
    plt.text(min(v + 500, 39500),
             b.get_y() + b.get_height()/2,
             f"{v:,}", va="center", fontsize=9)

plt.tight_layout()
plt.savefig("graph1_loyalty.png", dpi=120)


# =======================================================
# 2) Three labeled dots: Average recency vs Average frequency per segment
# =======================================================
seg_avg = (
    rfm.groupby("segment")[["recency", "frequency", "monetary"]]
       .mean()
       .reindex(order)
)

plt.figure(figsize=(7, 5))
colors = {"Loyal customers": "orange", "New customers": "lightgreen", "Inactive": "lightblue"}
for seg in order:
    x = seg_avg.loc[seg, "recency"]
    y = seg_avg.loc[seg, "frequency"]
    m = seg_avg.loc[seg, "monetary"]
    plt.scatter(x, y, s=160, color=colors[seg], edgecolor="black",
                label=f'Average "{seg}": {m:.2f}$')
# expand axes to ensure visibility
xmax = max(3, float(seg_avg["recency"].max()) * 1.3)
ymax = max(25, float(seg_avg["frequency"].max()) * 1.3)
plt.xlim(0, xmax)
plt.ylim(0, ymax)
plt.title("Average Frequency vs Average Recency by Segment")
plt.xlabel("Average Recency (months)")
plt.ylabel("Average Frequency")
plt.legend(loc="upper right")
plt.tight_layout()
plt.savefig("graph2_avg_freq_recency.png", dpi=120)

# =======================================================
# 3) Clusters — Frequency vs Monetary (sampled for cleaner look)
# =======================================================
# use original (unlogged) axes as requested; keep plotting to 0..100
plot_df = rfm.copy()
# optionally sample for display only (clustering still used all data)
max_points = 5000
if len(plot_df) > max_points:
    plot_df = plot_df.sample(max_points, random_state=42)

cmap = ["red", "blue", "green", "cyan", "pink"]
plt.figure(figsize=(7, 5))
for cid, col in enumerate(cmap):
    sub = plot_df[plot_df["cluster"] == cid]
    plt.scatter(sub["frequency"], sub["monetary"], s=18, color=col, label=f"Cluster {cid+1}", alpha=0.9)
plt.title("Clusters – Frequency vs Monetary Value")
plt.xlabel("Frequency (0 → 100)")
plt.ylabel("Monetary (0 → 100)")
plt.xlim(0, 100)
plt.ylim(0, 100)
plt.legend(loc="upper right")
plt.tight_layout()
plt.savefig("graph3_clusters_freq_monetary.png", dpi=120)

# =======================================================
# 4) PCA 2D projection of clusters + centroids (expanded limits; legend out of the way)
# =======================================================
pca = PCA(n_components=2, random_state=42)
p2 = pca.fit_transform(X_scaled)
rfm["pca1"], rfm["pca2"] = p2[:, 0], p2[:, 1]
cent2 = pca.transform(kmeans.cluster_centers_)

plt.figure(figsize=(7, 5))
for cid, col in enumerate(cmap):
    sub = rfm[rfm["cluster"] == cid]
    plt.scatter(sub["pca1"], sub["pca2"], s=18, color=col, label=f"Cluster {cid+1}", alpha=0.9)
plt.scatter(cent2[:, 0], cent2[:, 1], s=260, color="yellow", edgecolor="black",
            marker="o", label="Centroids")

# dynamic margins so all clusters & centroids are fully visible
x_min = min(rfm["pca1"].min(), cent2[:, 0].min())
x_max = max(rfm["pca1"].max(), cent2[:, 0].max())
y_min = min(rfm["pca2"].min(), cent2[:, 1].min())
y_max = max(rfm["pca2"].max(), cent2[:, 1].max())
pad_x = (x_max - x_min) * 0.15 + 0.5
pad_y = (y_max - y_min) * 0.15 + 0.5
plt.xlim(x_min - pad_x, x_max + pad_x)
plt.ylim(y_min - pad_y, y_max + pad_y)

plt.title("Clusters of Customers (PCA Projection)")
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.legend(loc="upper left", framealpha=0.9)
plt.tight_layout()
plt.savefig("graph4_clusters_pca.png", dpi=120)

# ---------- output ----------
if HEADLESS:
    print("\n[✔] Saved graphs:")
else:
    print("\n[INFO] Display available → Showing last graph.")
    plt.show()

for f in [
    "graph1_loyalty.png",
    "graph2_avg_freq_recency.png",
    "graph3_clusters_freq_monetary.png",
    "graph4_clusters_pca.png",
]:
    print("   ", os.path.abspath(f))
