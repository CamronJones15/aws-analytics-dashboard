-- trips_by_day.sql
-- Daily trip volume, average fare, and average duration
SELECT
    pickup_date,
    COUNT(*)                          AS trip_count,
    ROUND(AVG(fare_amount), 2)        AS avg_fare,
    ROUND(AVG(trip_duration_min), 1)  AS avg_duration_min
FROM nyc_taxi_processed
WHERE pickup_year = 2024
  AND pickup_month = 1
GROUP BY pickup_date
ORDER BY pickup_date;
