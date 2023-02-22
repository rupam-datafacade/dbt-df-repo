SELECT
  SUM(ABS("Qty")) as total_sales,
  SUM(ABS(total_amt)) as total_revenue,
  SUM(ABS(total_amt) - ABS("Tax")) as total_profit
FROM
  {{table}}
WHERE
  TO_TIMESTAMP(tran_date, 'YYYY-MM-DD') BETWEEN (CURRENT_DATE - INTERVAL '7 days')
  AND CURRENT_DATE;