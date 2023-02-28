SELECT "Store_type", COUNT(DISTINCT t.cust_id) AS new_customer_count
FROM {{transaction_table}} t
JOIN {{customer_segmentation_table}} cs ON t.cust_id = cs.cust_id
WHERE cs.customer_segment = 'New Customers'
GROUP BY "Store_type"
ORDER BY new_customer_count DESC
LIMIT {{total_platforms}};

