-- Creates table based on CSV and loads data

CREATE TABLE data_2022_oct (
    event_time TIMESTAMPTZ,
    event_type VARCHAR(20),
    product_id INTEGER,
    price NUMERIC(10,2),
    user_id BIGINT,
    user_session UUID
);

\copy data_2022_oct FROM './data_2022_oct.csv' DELIMITER ',' CSV HEADER;
