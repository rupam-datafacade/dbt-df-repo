import pandas as pd
import numpy as np

dim_customer = df_helper.get_table("public.dim_customer_table")
fact_order = df_helper.get_table("public.fact_order_table")
dim_customer_address = df_helper.get_table("public.dim_customer_address_table")

dim_customer['created_at'] = pd.to_datetime(dim_customer['created_at'])
fact_order['created_at'] = pd.to_datetime(fact_order['created_at'])
dim_customer_address['created_at'] = pd.to_datetime(
    dim_customer_address['created_at'])

reference_date = pd.to_datetime('2023-04-30')
window_length = 15

last_purchase_dates = fact_order.groupby(
    'customer_id')['created_at'].max().reset_index()
last_purchase_dates['DIFF_DATE'] = (
    reference_date - last_purchase_dates['created_at']).dt.days
last_purchase_dates['R_score'] = (
    (window_length - last_purchase_dates['DIFF_DATE']) / window_length) * 100

fact_order['purchase_date'] = fact_order['created_at'].dt.date
unique_purchase_days = fact_order.groupby(
    'customer_id')['purchase_date'].nunique().reset_index()
unique_purchase_days['F_score'] = (
    unique_purchase_days['purchase_date'] / window_length) * 100

scores = pd.merge(last_purchase_dates[['customer_id', 'R_score']], unique_purchase_days[[
                  'customer_id', 'F_score']], on='customer_id')

scores['Loyalty_Score'] = (scores['R_score'] * scores['F_score']) / (100**2)
scores['Loyalty_Score'] = np.where(
    scores['Loyalty_Score'] < 0, 0, scores['Loyalty_Score'])

scores['Churn'] = np.where(scores['Loyalty_Score'] > 0, 0, 1)

churned_customers = scores[scores['Churn'] == 1]

churned_customers_df = pd.merge(
    churned_customers, dim_customer[['id', 'first_name', 'last_name', 'email', 'Gender']], left_on='customer_id', right_on='id')

churned_customers_df = churned_customers_df[[
    'customer_id', 'first_name', 'last_name', 'email', 'Gender', 'Churn']]

churned_customers_with_address = pd.merge(
    churned_customers_df, dim_customer_address[['customer_id', 'country', 'region']], on='customer_id')

churn_by_segment = churned_customers_with_address.groupby(
    ['Gender', 'country', 'region']).size().reset_index(name='Churn_Count')

churn_by_segment = churn_by_segment.sort_values(
    'Churn_Count', ascending=False).reset_index(drop=True)

df_helper.publish(churn_by_segment.head(10))