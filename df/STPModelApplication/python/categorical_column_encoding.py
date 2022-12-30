import numpy as np
import pandas as pd
from dirty_cat import SimilarityEncoder
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

from dft.base_execution_handler import BaseExecutionHandler


class ExecutionHandler(BaseExecutionHandler):

    def execute(self, data: pd.DataFrame):
        columns = list(data.select_dtypes(include=['object']).columns)
        distinct_values = dict(map(lambda x: (x, len(pd.unique(data[x]))), columns))
        least_distinct_columns = list(dict(filter(lambda x: x[1] <= 5, distinct_values.items())).keys())
        mid_distinct_columns = list(dict(filter(lambda x: 5 < x[1] <= 10, distinct_values.items())).keys())
        most_distinct_values = list(dict(filter(lambda x: 10 < x[1], distinct_values.items())).keys())

        if len(least_distinct_columns):
            data = self.one_hot_encode(data, least_distinct_columns, drop_columns=True)
        if len(mid_distinct_columns):
            data = self.original_encode(data, mid_distinct_columns)
        if len(most_distinct_values):
            data = self.similarity_encode(data, most_distinct_values)

        return data

    def one_hot_encode(self, data: pd.DataFrame, columns, drop_columns):
        try:
            encoder = OneHotEncoder(sparse=False, handle_unknown='ignore').fit(data[columns])

            encoded_cols = list(encoder.get_feature_names_out(columns))

            data[encoded_cols] = encoder.transform(data[columns])
            if drop_columns:
                data = data.drop(columns, axis=1)

            for col in columns:
                print(col+" is "+"encoded")
            return data

        except Exception as e:
            raise type(e)(e)

    def original_encode(self, data: pd.DataFrame, columns):
        try:
            encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=np.nan).fit(data[columns])
            new_names = [column + '_' + 'encode' for column in columns]
            data[new_names] = pd.DataFrame(encoder.transform(data[columns]))
            data.drop(columns, axis=1, inplace=True)
            for col in columns:
                print(col+" is "+"encoded")
            return data
        except Exception as e:
            raise type(e)(e)

    def similarity_encode(self, data: pd.DataFrame, columns):
        try:
            for col in columns:
                encoder = SimilarityEncoder(similarity='ngram')
                encoded_df = pd.DataFrame(encoder.fit_transform(data[[col]]))
                encoded_df.columns = [col+'_'+str(i) for i in encoded_df.columns]
                data = pd.concat([data, encoded_df], axis=1)
                data.drop(col, axis=1, inplace=True)
                print(col + " is " + "encoded")

            return data
        except Exception as e:
            raise type(e)(e)
