"""
Inputs:
    - data: Transformed data  in the form of dataframe
    - method: segmentation method (Hierarchical/Agglomerative,Kmeans(default),Gaussian Mixture Model)
    - start: Number that specify number of segment to start with (must be >=1) (default is 2)
    - end: Number that specify number of segment for which the method will run at max with (default is 10)
Output:
    - Data with the metrics value for each choice of number of segments in the form of dataframe
"""
import pandas as pd
import sklearn
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn import metrics
import scipy.cluster.hierarchy as sch
import matplotlib.pyplot as plt
from dft import df_plot
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
import dirty_cat

from dft.base_execution_handler import BaseExecutionHandler


class ExecutionHandler(BaseExecutionHandler):
    def execute(self, data, CustomerID,  method='Kmeans', start=2, end=10):
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
                temp_data[data.columns] = data[data.columns]

            data = self.numeric_column_scale(data)
            data = self.categorical_column_encode(data)
            if method == 'Hierarchical/Agglomerative':
                plt.figure(1, figsize=(16, 8))

                dendrogram = sch.dendrogram(sch.linkage(data, method="ward"))

                plt.title('Dendrogram')
                plt.xlabel('Points')
                plt.ylabel('Euclidean distances')
                plt.show()
                df = pd.DataFrame()

            elif method == 'Kmeans':
                intra_segment_variance = []
                number_of_segments = range(start, end+1)
                for i in range(start, end + 1):
                    kmeans = KMeans(n_clusters=i, init='k-means++', random_state=100)
                    kmeans.fit(data)
                    intra_segment_variance.append(kmeans.inertia_)

                df = pd.DataFrame({'Number of Segments': number_of_segments,
                                   'Intra Segment Variance': intra_segment_variance})
                df_plot.line_chart('Elbow Plot', 'Number of Segments', 'Intra Segment Variance', df)

            elif method == 'Gaussian Mixture Model':
                S = []
                K = range(start, end + 1)

                for k in K:
                    model = GaussianMixture(n_components=k, n_init=20, init_params='kmeans')
                    labels = model.fit_predict(data)
                    S.append(metrics.silhouette_score(data, labels, metric='euclidean'))
                df = pd.DataFrame({'Number of Segments': K,
                                   'Silhouette Score': S})

                df_plot.line_chart('Silhouette Score Plot', 'Number of Segments', 'Silhouette Score', df)

        except Exception as e:
            raise type(e)(e)

        return df

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
