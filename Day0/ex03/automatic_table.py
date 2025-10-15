import psycopg2
import pandas as pd
import os
import uuid

def safe_uuid(value):
	"""
	Convert a value to a valid UUID or return None.
	"""
	try:
		return uuid.UUID(str(value))
	except Exception:
		return None

conn = psycopg2.connect(
	dbname="piscineds",
	user="gtskitis",
	password="mysecretpassword",
	host="localhost"
)
cur = conn.cursor()

# fixed schema
columns = {
	"event_time":   "TIMESTAMPTZ",
	"event_type":   "VARCHAR(20)",
	"product_id":   "INTEGER",
	"price":        "NUMERIC(10,2)",
	"user_id":      "BIGINT",
	"user_session": "UUID"
}

folder = "./customer"

import io

for file in os.listdir(folder):
    if file.endswith(".csv"):
        table_name = os.path.splitext(file)[0]
        csv_path = os.path.join(folder, file)
        print(f"Loading {csv_path}...")

        df = pd.read_csv(csv_path)

        cur.execute(f"DROP TABLE IF EXISTS {table_name};")
        cur.execute(f"""
        CREATE TABLE {table_name} (
            event_time   TIMESTAMPTZ,
            event_type   VARCHAR(20),
            product_id   INTEGER,
            price        NUMERIC(10,2),
            user_id      BIGINT,
            user_session UUID
        );
        """)

        # Clean dataframe (replace NaN with \N for NULLs)
        df = df.where(pd.notnull(df), None)

        # Write CSV content to memory buffer
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, header=False)
        buffer.seek(0)

        # Bulk copy directly into Postgres
        cur.copy_from(buffer, table_name, sep=",", null="")

        conn.commit()
        print(f"Created table {table_name} ({len(df):,} rows)")


conn.commit()
cur.close()
conn.close()
