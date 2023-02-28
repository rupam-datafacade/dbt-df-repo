SELECT pci.prod_cat, SUM(t."Qty") as total_sales
FROM {{transaction_table}} t
JOIN {{customer_segmentation_table}} cs ON t.cust_id = cs.cust_id
JOIN {{product_table}} pci ON t.prod_cat_code = pci.prod_cat_code
WHERE cs.customer_segment = 'New Customers'
GROUP BY pci.prod_cat
ORDER BY total_sales DESC
LIMIT {{total_number_product}};
