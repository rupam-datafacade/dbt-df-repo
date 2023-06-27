SELECT
  CASE
    WHEN DATEDIFF(
      'day',
      toDate(toDateTime("timestamp_datetime"), 'Asia/Kolkata'),
      toDate("departure_date", 'Asia/Kolkata')
    ) BETWEEN 0 AND 2
    THEN '0-2 days'
    WHEN DATEDIFF(
      'day',
      toDate(toDateTime("timestamp_datetime"), 'Asia/Kolkata'),
      toDate("departure_date", 'Asia/Kolkata')
    ) BETWEEN 3 AND 7
    THEN '3-7 days'
    WHEN DATEDIFF(
      'day',
      toDate(toDateTime("timestamp_datetime"), 'Asia/Kolkata'),
      toDate("departure_date", 'Asia/Kolkata')
    ) BETWEEN 8 AND 15
    THEN '8-15 days'
    WHEN DATEDIFF(
      'day',
      toDate(toDateTime("timestamp_datetime"), 'Asia/Kolkata'),
      toDate("departure_date", 'Asia/Kolkata')
    ) BETWEEN 16 AND 30
    THEN '16-30 days'
    WHEN DATEDIFF(
      'day',
      toDate(toDateTime("timestamp_datetime"), 'Asia/Kolkata'),
      toDate("departure_date", 'Asia/Kolkata')
    ) BETWEEN 31 AND 60
    THEN '31-60 days'
    WHEN DATEDIFF(
      'day',
      toDate(toDateTime("timestamp_datetime"), 'Asia/Kolkata'),
      toDate("departure_date", 'Asia/Kolkata')
    ) BETWEEN 61 AND 90
    THEN '61-90 days'
    ELSE '90+ days'
  END AS "apd_bucket",
  COUNT(*) AS "apd_count"
FROM "distributed"."flight_search"
WHERE
  toDate(toDateTime("timestamp_datetime"), 'Asia/Kolkata') >= toDate('2023-06-22', 'Asia/Kolkata')
  AND toDate(toDateTime("timestamp_datetime"), 'Asia/Kolkata') < toDate('2023-06-23', 'Asia/Kolkata')
GROUP BY
  "apd_bucket"