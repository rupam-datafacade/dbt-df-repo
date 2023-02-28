SELECT DISTINCT t.cust_id
FROM {{transaction_table}} t
JOIN {{customer_segmentation_table}} cs ON t.cust_id = cs.cust_id
WHERE cs.customer_segment = 'New Customers';
