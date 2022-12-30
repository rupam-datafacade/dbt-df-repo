"""
Action for converting source raw data to RFM model schema
Inputs:
    - Data: Source data in the form of Dataframe
    -CustomerID: column names to be provided by user(string)

Output:
    - Dataframe in the form of RFM model schema
"""
import traceback
import pandas as pd
from dft.base_execution_handler import BaseExecutionHandler


class ExecutionHandler(BaseExecutionHandler):
    def execute(self, Data):

        try:
            table = Data
            for col in list(table.select_dtypes(include=['object']).columns):
                if pd.to_datetime(table[col], errors='coerce').notnull().sum() > 0:
                    table.drop(col, axis=1, inplace=True)
                elif table[col].str.contains(
                        r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*").sum() > 0:
                    table.drop(col, axis=1, inplace=True)
                elif table[col].str.contains(
                        r"([A-Z][^\.!?]*[\.!?])").sum() > 0:
                    table.drop(col, axis=1, inplace=True)
                else:
                    pass
            for col in list(table.select_dtypes(include=['float']).columns):
                if table[col].astype(str).str.contains(
                        r"^(\+|-)?(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,6})?))$").sum() > 0:
                    table.drop(col, axis=1, inplace=True)
                elif table[col].astype(str).str.contains(
                        r"^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$").sum() > 0:
                    table.drop(col, axis=1, inplace=True)
                else:
                    pass

            return table
        except Exception as e:
            print(e)
            print(traceback.format_exc())
