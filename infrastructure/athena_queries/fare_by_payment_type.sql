-- fare_by_payment_type.sql
-- Compare trip volume and average fare across payment methods
-- Payment type: 1=Credit card, 2=Cash, 3=No charge, 4=Dispute
SELECT
    CASE payment_type
        WHEN 1 THEN 'Credit card'
        WHEN 2 THEN 'Cash'
        WHEN 3 THEN 'No charge'
        WHEN 4 THEN 'Dispute'
        ELSE 'Unknown'
    END                               AS payment_method,
    COUNT(*)                          AS trip_count,
    ROUND(AVG(fare_amount), 2)        AS avg_fare,
    ROUND(AVG(tip_amount), 2)         AS avg_tip,
    ROUND(SUM(total_amount), 2)       AS total_revenue
FROM nyc_taxi_processed
WHERE pickup_year = 2024
  AND pickup_month = 1
  AND fare_amount > 0
GROUP BY payment_type
ORDER BY trip_count DESC;
