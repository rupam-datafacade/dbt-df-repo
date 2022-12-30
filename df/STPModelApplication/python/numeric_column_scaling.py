"""
Inputs:
    - data: Source data in the form of dataframe
    - columns: List of column names on which you want to add transformation
Output:
    - Data in the form of dataframe with transformed columns
"""
import pandas as pd
from dft.base_execution_handler import BaseExecutionHandler


class ExecutionHandler(BaseExecutionHandler):
    def execute(self, data: pd.DataFrame):
        from sklearn.preprocessing import MinMaxScaler
        columns = list(data.select_dtypes(include=['int', 'float']).columns)
        for col in columns:
            if data[col].dtype == 'float':
                scaler = MinMaxScaler().fit(data[[col]])
                data[col] = scaler.transform(data[[col]])

                print(col + ' Is Normalized')
            else:
                if data[col].nunique()/len(data[col]) > 0.5:
                    scaler = MinMaxScaler().fit(data[[col]])
                    data[col] = scaler.transform(data[[col]]).round(2)
                    print(col + ' Is Normalized')
                else:
                    dummies = pd.get_dummies(data[col])
                    dummies.columns = [col+'_'+str(i) for i in list(dummies.columns)]
                    data = pd.concat([data, dummies], axis=1)
                    data = data.drop(col, axis=1)
                    print(col + ' Is Normalized')

        return data
