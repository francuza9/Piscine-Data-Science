-- Create a table "items" using columns from items.csv

CREATE TABLE items (
    product_id INTEGER,              -- small numeric IDs
    category_id BIGINT,              -- larger numeric IDs
    category_code TEXT,              -- category strings (nullable)
    brand VARCHAR(50)                -- short text
);

\copy items FROM './item.csv' DELIMITER ',' CSV HEADER;
