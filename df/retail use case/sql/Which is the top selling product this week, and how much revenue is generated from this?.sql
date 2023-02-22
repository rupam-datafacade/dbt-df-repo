SELECT p.prod_cat, SUM(t."Qty") as total_sales
FROM {{transaction_table}} t
JOIN {{product_table}} p ON t.prod_cat_code = p.prod_cat_code
WHERE TO_TIMESTAMP(t.tran_date,'YYYY-MM-DD') BETWEEN (CURRENT_DATE - INTERVAL '7 days') AND CURRENT_DATE
GROUP BY p.prod_cat
ORDER BY total_sales DESC
LIMIT {{total_number_product}};