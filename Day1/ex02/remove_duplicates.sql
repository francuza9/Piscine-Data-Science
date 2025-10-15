DROP TABLE IF EXISTS customers_nodup;

CREATE TABLE customers_nodup AS
SELECT *
FROM (
  SELECT *,
         LAG(event_time) OVER (
           PARTITION BY event_type, product_id, price, user_id, user_session
           ORDER BY event_time
         ) AS prev_time
  FROM customers
) t
WHERE prev_time IS NULL
   OR event_time - prev_time > interval '1 second';

DROP TABLE IF EXISTS customers;
ALTER TABLE customers_nodup RENAME TO customers;
