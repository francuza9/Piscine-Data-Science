BEGIN;

DROP TABLE IF EXISTS fusion;

CREATE TABLE fusion AS
SELECT
    c.event_time,
    c.event_type,
    c.product_id,
    c.price        AS event_price,
    c.user_id,
    c.user_session,
    i.category_id,
    i.category_code,
    i.brand
FROM customers AS c
LEFT JOIN items AS i
    ON c.product_id = i.product_id;

DROP TABLE IF EXISTS customers;
ALTER TABLE fusion RENAME TO customers;

COMMIT;
