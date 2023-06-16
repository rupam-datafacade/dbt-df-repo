
import pandas as pd
import numpy as np

dim_customer = df_helper.get_table("public.dim_customer_table")
fact_order = df_helper.get_table("public.fact_order_table")

dim_customer['created_at'] = pd.to_datetime(dim_customer['created_at'])
fact_order['created_at'] = pd.to_datetime(fact_order['created_at'])

reference_date = pd.to_datetime('2023-04-30')
window_length = 15

# R-score calculation
last_purchase_dates = fact_order.groupby(
    'customer_id')['created_at'].max().reset_index()
last_purchase_dates['DIFF_DATE'] = (
    reference_date - last_purchase_dates['created_at']).dt.days
last_purchase_dates['R_score'] = (
    (window_length - last_purchase_dates['DIFF_DATE']) / window_length) * 100

# F-score calculation
fact_order['purchase_date'] = fact_order['created_at'].dt.date
unique_purchase_days = fact_order.groupby(
    'customer_id')['purchase_date'].nunique().reset_index()
unique_purchase_days['F_score'] = (
    unique_purchase_days['purchase_date'] / window_length) * 100

# Merge R-score and F-score
scores = pd.merge(last_purchase_dates[['customer_id', 'R_score']], unique_purchase_days[[
    'customer_id', 'F_score']], on='customer_id')

# Loyalty Score calculation
scores['Loyalty_Score'] = (
    scores['R_score'] * scores['F_score']) / (100**2)
scores['Loyalty_Score'] = np.where(
    scores['Loyalty_Score'] < 0, 0, scores['Loyalty_Score'])

# Churn calculation
scores['Churn'] = np.where(scores['Loyalty_Score'] > 0, 0, 1)

# Churn rate calculation
churn_rate = (scores['Churn'].sum() / len(scores)) * 100

churn_rate_df = pd.DataFrame({'Churn_Rate': [churn_rate]})

# publish final result as pandas dataframe
df_helper.publish(churn_rate_df)
