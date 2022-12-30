""""
Action for getting the summary of the RFM values for each segment
Inputs:
    - data: Dataframe with the segments and all the features
    - segment_column: Name of the column to be used as segment
Output:
    - Dataframe with count of  each segments
"""
import pandas as pd
from dft import df_plot


from dft.base_execution_handler import BaseExecutionHandler


class ExecutionHandler(BaseExecutionHandler):
    def execute(self, data, segment_column='segment'):
        try:
            data[segment_column] = ['Segment '+str(i+1) for i in data[segment_column]]
            table = data.groupby([segment_column]).agg({
                data.columns[1]: 'count'
            }).round(0)
            table = table.reset_index()
            table.columns = ['Segment', 'Segment Count']
            df_plot.pie_chart('Segment Count', 'Segment', 'Segment Count', table)

        except Exception as e:
            raise type(e)(e)

        return table
