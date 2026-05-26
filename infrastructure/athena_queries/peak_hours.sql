-- peak_hours.sql
-- Identify peak demand hours by day of week
-- Useful for understanding surge pricing patterns
SELECT
    DAY_OF_WEEK(date_parse(CAST(pickup_date AS VARCHAR), '%Y-%m-%d')) AS day_of_week,
    CASE DAY_OF_WEEK(date_parse(CAST(pickup_date AS VARCHAR), '%Y-%m-%d'))
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
        WHEN 7 THEN 'Sunday'
    END                               AS day_name,
    pickup_hour,
    COUNT(*)                          AS trip_count,
    ROUND(AVG(fare_amount), 2)        AS avg_fare
FROM nyc_taxi_processed
WHERE pickup_year = 2024
  AND pickup_month = 1
GROUP BY 1, 2, 3
ORDER BY day_of_week, pickup_hour;
