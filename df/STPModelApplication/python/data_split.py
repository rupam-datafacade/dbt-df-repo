"""
Inputs:
    - data: Source data in the form of dataframe
    - columns: List of column names on which you want to subset the data
Output:
    - Data in the form of dataframe with the subset of columns
"""
import pandas as pd


from dft.base_execution_handler import BaseExecutionHandler


class ExecutionHandler(BaseExecutionHandler):
    def execute(self, data: pd.DataFrame, columns: [str]):
        if '' not in columns:
            pass
        else:
            columns.remove('')

        if len(columns) > 0:
            data = data[columns]
            print('The Resultant Data Has The Following Columns')
            for col in columns : print(col)
        else:
            print('No Columns Selected,The Data Remains Same')
            data = data

        return data
