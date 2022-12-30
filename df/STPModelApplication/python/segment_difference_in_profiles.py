"""
Inputs:
    - data: Transformed data  in the form of dataframe
    - segment_column: Name of the column to be used as segment
Output:
    - Data in the form of dataframe with values indicating if the segment difference for each feature is significant
      (2:significant,1:not significant,0: significant in the negative side)
"""
import pandas as pd
from dft.base_execution_handler import BaseExecutionHandler


class ExecutionHandler(BaseExecutionHandler):
    def execute(self, data, CustomerID, segment_column='segment'):
        try:
            if '' not in CustomerID:
                pass
            else:
                CustomerID.remove('')
            if len(CustomerID) > 0:
                if data[CustomerID].duplicated().sum() == 0:
                    data = data.drop(CustomerID, axis=1)
                else:
                    print("The Customer ID Must Have All Unique Values")
                    raise
            else:
                data = data.drop('ID', axis=1)
            columns = list(data.select_dtypes(include=['int', 'float']).columns.drop(segment_column))
            if len(columns) > 1:
                for col in columns:
                    data[col] = data[col] - data[col].mean()
                df_segment_means = data.groupby([segment_column]).mean()

                for col in df_segment_means.columns:
                    df_segment_means[col] = df_segment_means[col].apply(
                        lambda x: 2 if x > data[col].std() else (1 if 0 < x < data[col].std() else 0))

                df_segment_means = df_segment_means.reset_index()
            else:
                df_segment_means = pd.DataFrame()

        except Exception as e:
            raise type(e)(e)

        return df_segment_means
