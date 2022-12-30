"""
Inputs:
    - data: Transformed data  in the form of dataframe
    - method: segmentation method (Hierarchical/Agglomerative,Kmeans(default),Gaussian Mixture Model)
    - number_of_segments: Number of segment (default is 2)
Output:
    - Data in the form of dataframe with the segment labels in a separate column
"""
import statsmodels.api as sm
import dirty_cat
import numpy as np
import pandas as pd
import sklearn
from dft import df_plot
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from dft.base_execution_handler import BaseExecutionHandler


class ExecutionHandler(BaseExecutionHandler):
    def execute(self, data, CustomerID, method='Kmeans', number_of_segments=2):
        try:
            if '' not in CustomerID:
                pass
            else:
                CustomerID.remove('')
            if len(CustomerID) > 0:
                if data[CustomerID].duplicated().sum() == 0:
                    temp_data = pd.DataFrame()
                    temp_data[CustomerID] = data[CustomerID]
                    data = data.drop(CustomerID, axis=1)
                    temp_data[data.columns] = data[data.columns]
                else:
                    print("The Customer ID Must Have All Unique Values")
                    raise
            else:
                CustomerID = range(1, len(data[data.columns[0]]) + 1)
                temp_data = pd.DataFrame()
                temp_data['ID'] = CustomerID
                CustomerID = ['ID']
                temp_data[data.columns] = data[data.columns]

            data = self.numeric_column_scale(data)
            data = self.categorical_column_encode(data)
            if method == 'Hierarchical/Agglomerative':
                model = AgglomerativeClustering(n_clusters=number_of_segments, affinity='euclidean', linkage='ward')
                segment = model.fit_predict(data)

            elif method == 'Kmeans':
                model = KMeans(n_clusters=number_of_segments, init='k-means++', random_state=100)
                model.fit(data)
                segment = model.labels_

            elif method == 'Gaussian Mixture Model':
                model = GaussianMixture(n_components=number_of_segments,  # the number of clusters
                                        max_iter=100,  # the number of EM iterations to perform
                                        init_params='kmeans', random_state=100)
                model.fit(data)
                segment = model.predict(data)
            y_train = segment
            X_train = data
            res = sm.OLS(y_train, X_train, family=sm.families.Binomial()).fit()
            res.summary()
            df_res = pd.DataFrame({
                'param_name': res.params.keys()
                , 'param_w': res.params.values
                , 'pval': res.pvalues
            })
            df_res['abs_param_w'] = np.abs(df_res['param_w'])
            # marking field is significant under 95% confidence interval
            df_res['is_sig_95'] = (df_res['pval'] < 0.05)
            range_per_feature = dict()
            for col in temp_data.drop(CustomerID, axis=1).columns:
                range_per_feature[col] = list()
                for key, coeff in res.params.items():
                    if col in key:
                        feature = col
                        range_per_feature[feature].append(coeff)
            importance_per_feature = {
                k: max(v) - min(v) for k, v in range_per_feature.items()
            }

            # compute relative importance per feature
            # or normalized feature importance by dividing
            # sum of importance for all features
            total_feature_importance = sum(importance_per_feature.values())
            relative_importance_per_feature = {
                k: 100 * round(v / total_feature_importance, 3) for k, v in importance_per_feature.items()
            }
            df = pd.DataFrame()
            df['Features'] = relative_importance_per_feature.keys()
            df['Relative Importance'] = relative_importance_per_feature.values()
            df.sort_values(by='Relative Importance', inplace=True, ascending=False)
            df_plot.bar_chart('Feature Importance', df.columns[0], df.columns[1], df)
            temp_data['segment'] = segment

        except Exception as e:
            raise type(e)(e)

        return temp_data

    def categorical_column_encode(self, data: pd.DataFrame):
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
                print(col + " is " + "encoded")
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
                print(col + " is " + "encoded")
            return data
        except Exception as e:
            raise type(e)(e)

    def similarity_encode(self, data: pd.DataFrame, columns):
        try:
            for col in columns:
                encoder = dirty_cat.SimilarityEncoder(similarity='ngram')
                encoded_df = pd.DataFrame(encoder.fit_transform(data[[col]]))
                encoded_df.columns = [col + '_' + str(i) for i in encoded_df.columns]
                data = pd.concat([data, encoded_df], axis=1)
                data.drop(col, axis=1, inplace=True)
                print(col + " is " + "encoded")

            return data
        except Exception as e:
            raise type(e)(e)

    def numeric_column_scale(self, data: pd.DataFrame):
        from sklearn.preprocessing import MinMaxScaler
        columns = list(data.select_dtypes(include=['int', 'float']).columns)
        for col in columns:
            if data[col].dtype == 'float':
                scaler = MinMaxScaler().fit(data[[col]])
                data[col] = scaler.transform(data[[col]])

                print(col + ' Is Normalized')
            else:
                if data[col].nunique() / len(data[col]) > 0.5:
                    scaler = MinMaxScaler().fit(data[[col]])
                    data[col] = scaler.transform(data[[col]]).round(2)
                    print(col + ' Is Normalized')
                else:
                    dummies = pd.get_dummies(data[col])
                    dummies.columns = [col + '_' + str(i) for i in list(dummies.columns)]
                    data = pd.concat([data, dummies], axis=1)
                    data = data.drop(col, axis=1)
                    print(col + ' Is Normalized')

        return data
