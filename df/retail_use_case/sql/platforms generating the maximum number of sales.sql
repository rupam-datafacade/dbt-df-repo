SELECT "Store_type", COUNT(ABS("Qty")) as total_number_sales
FROM {{table}}
WHERE TO_TIMESTAMP(tran_date, 'DD-MM-YYYY') BETWEEN (CURRENT_DATE - INTERVAL '7 days') AND CURRENT_DATE
GROUP BY "Store_type"
ORDER BY total_number_sales DESC
LIMIT {{number_of_platforms}};
