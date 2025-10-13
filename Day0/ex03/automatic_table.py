#!/usr/bin/env python3
import os
import csv
import psycopg2

# ---------- CONFIGURATION ----------
DB_NAME = "piscineds"
DB_USER = "gtskitis"                 # <-- replace with your 42 login
DB_PASS = "mysecretpassword"
DB_HOST = "localhost"
CUSTOMER_DIR = "./customer"
# -----------------------------------


def infer_pg_type(value: str) -> str:
    """Guess PostgreSQL type from a sample string value."""
    if value == "" or value is None:
        return "TEXT"  # fallback if empty
    lower = value.lower()
    if lower in ("true", "false"):
        return "BOOLEAN"
    try:
        int(value)
        return "INTEGER"
    except ValueError:
        pass
    try:
        float(value)
        return "NUMERIC"
    except ValueError:
        pass
    if ":" in value and "-" in value:  # e.g. '2023-01-01 00:00:00'
        return "TIMESTAMP"
    return "TEXT"


def create_table_from_csv(cursor, table_name, csv_path):
    """Read one CSV, infer schema, and create a matching SQL table."""
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        first_row = next(reader, None)

    # Infer each column type
    col_types = []
    for i, col in enumerate(headers):
        sample_value = first_row[i] if first_row else ""
        pg_type = infer_pg_type(sample_value)
        col_types.append((col.strip(), pg_type))

    # Build CREATE TABLE statement
    columns_sql = ", ".join(f'"{n}" {t}' for n, t in col_types)
    sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_sql});'
    cursor.execute(sql)
    print(f"Created table: {table_name}")


def copy_csv_into_table(cursor, table_name, csv_path):
    """Efficiently load CSV data into an existing table."""
    with open(csv_path, 'r', encoding='utf-8') as f:
        cursor.copy_expert(
            sql=f'COPY "{table_name}" FROM STDIN WITH (FORMAT csv, HEADER true)',
            file=f
        )
    print(f"Imported data into: {table_name}")


def main():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST
    )
    cur = conn.cursor()

    for file in os.listdir(CUSTOMER_DIR):
        if file.endswith(".csv"):
            table_name = file[:-4]  # strip .csv
            path = os.path.join(CUSTOMER_DIR, file)
            create_table_from_csv(cur, table_name, path)
            copy_csv_into_table(cur, table_name, path)
            conn.commit()

    cur.close()
    conn.close()
    print("All CSV files processed successfully!")


if __name__ == "__main__":
    main()
