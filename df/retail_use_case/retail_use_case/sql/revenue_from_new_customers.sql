SELECT SUM(ABS(t.total_amt)) AS total_revenue
FROM {{transaction_table}} t
JOIN {{customer_segmentation_table}} cs ON t.cust_id = cs.cust_id
WHERE cs.customer_segment = 'New Customers';
