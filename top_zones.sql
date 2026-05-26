-- top_zones.sql
-- Top 10 most active pickup zones
SELECT
    PULocationID  AS zone_id,
    COUNT(*)      AS pickups
FROM nyc_taxi_processed
WHERE pickup_year = 2024
  AND pickup_month = 1
GROUP BY PULocationID
ORDER BY pickups DESC
LIMIT 10;
