"""
Inputs:
    - data: Transformed data  in the form of dataframe
    - segment_column: Name of the column to be used as segment
Output:
    - Data in the form of dataframe with means of each features for all the segments and whole population
"""
import pandas as pd
from dft.base_execution_handler import BaseExecutionHandler


class ExecutionHandler(BaseExecutionHandler):
    def execute(self, data, CustomerID, segment_column='segment'):
        def max_count(x):

            return x.value_counts().index[0]
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
            columns = list(data.select_dtypes(include=['int', 'float']).columns)
            if len(columns) > 1:
                df_segment_means = data[columns].groupby([segment_column]).mean()
                for i in df_segment_means.columns:
                    df_segment_means.loc['population', i] = df_segment_means.mean()[i]
                df_segment_means = df_segment_means.reset_index()
            else:
                df_segment_means = pd.DataFrame()

            columns = list(data.select_dtypes(include=['object']).columns)
            columns.append(segment_column)
            if len(columns) > 1:
                df_segment_means2 = data[columns].groupby(segment_column).agg(max_count)
                for i in df_segment_means2.columns:
                    df_segment_means2.loc['population', i] = max_count(df_segment_means2[i])
                df_segment_means2 = df_segment_means2.reset_index().drop(segment_column, axis=1)
            else:
                df_segment_means2 = pd.DataFrame()

            df_segment_means = pd.concat([df_segment_means, df_segment_means2], axis=1)

        except Exception as e:
            raise type(e)(e)

        return df_segment_means
