-- SQLite examples for a table imported from cleaned_traffic_data.csv.
-- Import the CSV with table name `traffic`. date_time is ISO-formatted text.

-- Average traffic by hour of day.
SELECT hour, AVG(traffic_volume) AS average_traffic_volume
FROM traffic
GROUP BY hour
ORDER BY hour;

-- Average traffic by high-level weather category.
SELECT weather_main, AVG(traffic_volume) AS average_traffic_volume,
       COUNT(*) AS record_count
FROM traffic
GROUP BY weather_main
ORDER BY average_traffic_volume DESC;

-- Weekday versus weekend average traffic.
SELECT day_type, AVG(traffic_volume) AS average_traffic_volume,
       COUNT(*) AS record_count
FROM traffic
GROUP BY day_type
ORDER BY day_type;

-- Busiest month by average traffic volume (month values are 1-12).
SELECT month, month_name, AVG(traffic_volume) AS average_traffic_volume
FROM traffic
GROUP BY month, month_name
ORDER BY average_traffic_volume DESC
LIMIT 1;

-- Peak individual hourly traffic records.
SELECT date_time, traffic_volume, weather_main, holiday
FROM traffic
ORDER BY traffic_volume DESC, date_time
LIMIT 20;

-- Holiday versus non-holiday traffic. Holiday names other than No Holiday
-- are treated as holidays; check the record_count before comparing means.
SELECT CASE WHEN holiday = 'No Holiday' THEN 'Non-holiday' ELSE 'Holiday' END AS day_group,
       AVG(traffic_volume) AS average_traffic_volume,
       COUNT(*) AS record_count
FROM traffic
GROUP BY day_group
ORDER BY day_group;

-- Top weather categories by average traffic (at least 100 records).
SELECT weather_main, AVG(traffic_volume) AS average_traffic_volume,
       COUNT(*) AS record_count
FROM traffic
GROUP BY weather_main
HAVING COUNT(*) >= 100
ORDER BY average_traffic_volume DESC
LIMIT 10;