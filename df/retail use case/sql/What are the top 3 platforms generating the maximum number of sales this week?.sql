SELECT Store_type, COUNT(ABS("Qty")) as total_number_sales
FROM {{tabl}}
GROUP BY Store_type
WHERE TO_TIMESTAMP(tran_date, 'YYYY-MM-DD') BETWEEN (CURRENT_DATE - INTERVAL '7 days') AND CURRENT_DATE
ORDER BY total_number_sales DESC
LIMIT {{number_of_platforms}};
