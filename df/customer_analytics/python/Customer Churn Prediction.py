import pandas as pd 
import traceback
from datetime import date
import numpy as np
from lifetimes import BetaGeoFitter, GammaGammaFitter

df = df_helper.get_table(parameter_name="input_table", parameter_display_name="Input Table", parameter_description="Input Raw Table") 
id_customer = df_helper.get_column_list(parameter_name="id_customer", parameter_display_name="Customer ID", parameter_description=" Customer ID is the column(s) in the data set with customer identification number, phone number or email id that uniquely identifies the customer.")
id_interaction = df_helper.get_column("id_interaction","Interaction ID","The column with the interaction identification number or interaction date time stamp that uniquely identifies the purchase.")
ts_interaction = df_helper.get_column("ts_interaction","Interaction Date"," The column with the interaction date i.e date that was captured by the system when the customer made the interaction.")
n_interaction_value = df_helper.get_column("n_interaction_value","Interaction Value","The column with the interaction values that lists the interaction amount the customer for each interaction.")
is_churn =df_helper.get_string("is_churn", "Do you want to see only churned customer(opltional)", "Please select 'Yes' if want to see only churned customer")
# CONFIGS
penalize_coefficient = 0.5
period = 6
churn_threshold = 0.95


try:
    #Schema Creation
    table = pd.DataFrame()
    table[id_customer] = df[id_customer]
    table[[ts_interaction, n_interaction_value]] = df[[ts_interaction, n_interaction_value]]
    table[id_interaction] = df[id_interaction]
    table[n_interaction_value] = table[n_interaction_value].astype(float)
    table[ts_interaction] = pd.to_datetime(table[ts_interaction], infer_datetime_format=True)
    for i in id_customer:
        print(i+' Is Taken As id_customer For The Model Schema')
    print(id_interaction + ' Is Taken As id_interaction For The Model Schema')
    print(ts_interaction + ' Is Taken As ts_interaction For The Model Schema')
    print(n_interaction_value + ' Is Taken As n_interaction_value For The Model Schema')

    # RFM Calculation
    ts_reference = pd.to_datetime(date.today())
    today = pd.to_datetime(date.today())    
    # Calculation of RFM values
    table = table.groupby(id_customer).agg(
        {ts_interaction: [lambda d: (ts_reference - d.max()).days,  # Recency
                          lambda d: (today - d.min()).days],
         id_interaction: lambda num: num.count(),  # Frequency
         n_interaction_value: [  # Monetary
                               lambda value: abs(value).mean()
                              ]})
    table.columns = table.columns.droplevel(0)
    table.columns = ['Recency', "T", 'Frequency', "Monetary"]
    table["Frequency"] = table["Frequency"].astype(int)
    table = table.reset_index().dropna()

    # Churn Prediction
    recency = 'Recency'
    frequency = 'Frequency'
    monetary_value = "Monetary"
    t_first_interaction = "T"

    btyd = pd.DataFrame()
    alpha = penalize_coefficient
    if (any(table[recency] == 0) is True) or (any(table[frequency] == 0) is True) or (
        any(table[monetary_value] == 0) is True) or (any(table[t_first_interaction] == 0) is True):
        raise "Calculation is not possible, Recency,Frequency,Monetary Value and value of T must be > 0 "

    btyd[id_customer] = table[id_customer]
    bgf = BetaGeoFitter(penalizer_coef=alpha)
    bgf.fit(table[frequency], table[recency], table[t_first_interaction])

    btyd['churn_rate'] = 1 - bgf.conditional_probability_alive(table[frequency], table[recency],
                                                               table[t_first_interaction])

    btyd['is_churned'] = btyd['churn_rate'].apply(lambda x: True if x > churn_threshold else False)
    if is_churn == None:
         pass
    else:
        if is_churn == 'Yes':
            btyd = btyd.query(f'is_churned == True')
        else:
            btyd = btyd.query(f'is_churned == False')

except Exception as e:
    print(traceback.format_exc())
    raise e

df_helper.publish(btyd)