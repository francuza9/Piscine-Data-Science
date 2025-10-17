import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import psycopg2
import socket

def has_display():
    """Check if a display is really available (not just DISPLAY env set)."""
    display = os.environ.get("DISPLAY")
    if not display:
        return False
    # If DISPLAY exists but cannot connect, treat as headless
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(display)
        s.close()
        return True
    except Exception:
        return False

# --- Detect environment safely ---
if not has_display():
    matplotlib.use("Agg")
    HEADLESS = True
else:
    HEADLESS = False

# --- Database connection ---
conn = psycopg2.connect(
    host="localhost",
    dbname="piscineds",
    user="gtskitis",
    password="mysecretpassword"
)

# --- Query ---
query = """
SELECT event_type, COUNT(*) AS count
FROM customers
GROUP BY event_type
ORDER BY count DESC;
"""
df = pd.read_sql_query(query, conn)
conn.close()

# --- Plot ---
plt.figure(figsize=(7, 7))
plt.pie(df["count"], labels=df["event_type"], autopct="%1.1f%%", startangle=140)
plt.title("User actions on the website")

if HEADLESS:
    output_path = os.path.join(os.path.dirname(__file__), "pie_chart.png")
    plt.savefig(output_path)
    print(f"[✔] No display detected → chart saved as {output_path}")
else:
    print("[INFO] Display available → showing chart window.")
    plt.show()
