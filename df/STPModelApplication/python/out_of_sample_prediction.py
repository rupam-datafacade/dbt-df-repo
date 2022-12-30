"""
Inputs:
    - segment_data: Data  in the form of dataframe with the segment labels
    - segment_column: Name of the column to be used as segment
    - descriptor_data: Data to be used for segment description
    - method: Classification model to be used("Decision Tree Classifier,Logistic Regression(default),Random Forest Classifier,XGBoost Classifier")
    - out_of_sample_data: Data in the form of dataframe for which user want prediction
Outputs:
    - Confusion matrix and its plot
    - Predicted segment labels for the descriptor_data
"""
import pandas as pd
import sklearn.metrics
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
import numpy as np
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
import dirty_cat

from dft.base_execution_handler import BaseExecutionHandler


class ExecutionHandler(BaseExecutionHandler):
    def execute(self, segment_data, CustomerID, segment_column='segment', descriptor_data=None, method='Logistic Regression', out_of_sample_data=None):
        try:
            if '' not in CustomerID:
                pass
            else:
                CustomerID.remove('')
            if len(CustomerID) > 0:
                if descriptor_data[CustomerID].duplicated().sum() == 0:
                    temp_data = pd.DataFrame()
                    temp_sample_data = pd.DataFrame()
                    temp_data[CustomerID] = descriptor_data[CustomerID]
                    sample_CustomerID = [value for value in CustomerID if value in out_of_sample_data.columns]
                    if len(sample_CustomerID) > 0:
                        temp_sample_data[sample_CustomerID] = out_of_sample_data[sample_CustomerID]
                        out_of_sample_data = out_of_sample_data.drop(sample_CustomerID, axis=1)
                    else:
                        temp_sample_data['ID'] = range(1, len(out_of_sample_data[out_of_sample_data.columns[0]]) + 1)
                        sample_CustomerID = ['ID']
                    descriptor_data = descriptor_data.drop(CustomerID, axis=1)
                    temp_data[descriptor_data.columns] = descriptor_data[descriptor_data.columns]

                else:
                    print("The Customer ID Must Have All Unique Values")
                    raise
            else:
                CustomerID = range(1, len(descriptor_data[descriptor_data.columns[0]]) + 1)
                sample_CustomerID = range(len(descriptor_data[descriptor_data.columns[0]]),
                                          len(out_of_sample_data[out_of_sample_data.columns[0]]) +
                                          len(descriptor_data[descriptor_data.columns[0]]))
                temp_data = pd.DataFrame()
                temp_sample_data = pd.DataFrame()
                temp_data['ID'] = CustomerID
                temp_sample_data['ID'] = sample_CustomerID
                sample_CustomerID = ['ID']
                temp_data[descriptor_data.columns] = descriptor_data[descriptor_data.columns]
            descriptor_data_rows = descriptor_data.shape[0]
            data = pd.concat([descriptor_data, out_of_sample_data], axis=0).fillna(0)
            data = self.numeric_column_scale(data)
            data = self.categorical_column_encode(data)
            descriptor_data = data[:descriptor_data_rows]
            out_of_sample_data = data[descriptor_data_rows:]
            X_train = descriptor_data
            y_train = segment_data[segment_column]
            if method == 'Logistic Regression':
                model = LogisticRegression(multi_class='multinomial', solver='sag', penalty='l2', random_state=100,
                                           C=0.8, max_iter=1000)
                model.fit(X_train, y_train)
                cm = pd.crosstab(y_train, model.predict(X_train), rownames=['Actual'], colnames=['Predicted']
                                 , margins=True)  # Confusion Matrix
                print('Confusion Matrix:')
                print('')
                print(cm)
                print('')
                report = sklearn.metrics.classification_report(y_train, model.predict(X_train))  # Model Validation Report
                print('Model Validation Report:')
                print('')
                print(report)
                if out_of_sample_data is not None:
                    out_of_sample_prediction = pd.DataFrame(model.predict_proba(out_of_sample_data))
                    columns = ['Propensity' + '(Segment ' + str(i) + ')' for i in range(y_train.min(), y_train.max() + 1)]
                    out_of_sample_prediction.columns = columns
                    out_of_sample_prediction['Predicted'] = model.predict(out_of_sample_data)
                    out_of_sample_prediction = pd.concat([temp_sample_data[sample_CustomerID], out_of_sample_prediction],
                                                         axis=1)

            elif method == 'Decision Tree Classifier':
                model = DecisionTreeClassifier(max_depth=5, max_leaf_nodes=5,
                                               random_state=100)
                model.fit(X_train, y_train)
                cm = pd.crosstab(y_train, model.predict(X_train), rownames=['Actual'], colnames=['Predicted']
                                 , margins=True)  # Confusion Matrix
                print('Confusion Matrix:')
                print('')
                print(cm)
                print('')
                report = sklearn.metrics.classification_report(y_train, model.predict(X_train))  # Model Validation Report
                print('Model Validation Report:')
                print('')
                print(report)
                if out_of_sample_data is not None:
                    out_of_sample_prediction = pd.DataFrame(model.predict_proba(out_of_sample_data))
                    columns = ['Propensity' + '(Segment ' + str(i) + ')' for i in range(y_train.min(), y_train.max() + 1)]
                    out_of_sample_prediction.columns = columns
                    out_of_sample_prediction['Predicted'] = model.predict(out_of_sample_data)
                    out_of_sample_prediction = pd.concat([temp_sample_data[sample_CustomerID], out_of_sample_prediction],
                                                         axis=1)

            elif method == 'Random Forest Classifier':
                model = RandomForestClassifier(n_jobs=-1, random_state=42, max_depth=5,
                                               max_leaf_nodes=5)
                model.fit(X_train, y_train)
                cm = pd.crosstab(y_train, model.predict(X_train), rownames=['Actual'], colnames=['Predicted']
                                 , margins=True)  # Confusion Matrix
                print('Confusion Matrix:')
                print('')
                print(cm)
                print('')
                report = sklearn.metrics.classification_report(y_train, model.predict(X_train))  # Model Validation Report
                print('Model Validation Report:')
                print('')
                print(report)
                if out_of_sample_data is not None:
                    out_of_sample_prediction = pd.DataFrame(model.predict_proba(out_of_sample_data))
                    columns = ['Propensity' + '(Segment ' + str(i) + ')' for i in range(y_train.min(), y_train.max() + 1)]
                    out_of_sample_prediction.columns = columns
                    out_of_sample_prediction['Predicted'] = model.predict(out_of_sample_data)
                    out_of_sample_prediction = pd.concat([temp_sample_data[sample_CustomerID], out_of_sample_prediction],
                                                         axis=1)

            else:
                model = XGBClassifier(random_state=100, n_jobs=-1, n_estimators=10, max_depth=5,
                                      use_label_encoder=False,
                                      learning_rate=1, eval_metric='logloss')
                model.fit(X_train, y_train)
                cm = pd.crosstab(y_train, model.predict(X_train), rownames=['Actual'], colnames=['Predicted']
                                 , margins=True)  # Confusion Matrix
                print('Confusion Matrix:')
                print('')
                print(cm)
                print('')
                report = sklearn.metrics.classification_report(y_train, model.predict(X_train))  # Model Validation Report
                print('Model Validation Report:')
                print('')
                print(report)
                if out_of_sample_data is not None:
                    out_of_sample_prediction = pd.DataFrame(model.predict_proba(out_of_sample_data))
                    columns = ['Propensity' + '(Segment ' + str(i) + ')' for i in range(y_train.min(), y_train.max() + 1)]
                    out_of_sample_prediction.columns = columns
                    out_of_sample_prediction['Predicted'] = model.predict(out_of_sample_data)
                    out_of_sample_prediction = pd.concat([temp_sample_data[sample_CustomerID], out_of_sample_prediction], axis=1)

        except Exception as e:
            raise type(e)(e)

        return out_of_sample_prediction

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
