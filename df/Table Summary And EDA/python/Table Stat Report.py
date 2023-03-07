import pandas as pd
import numpy as np
from scipy.stats import kurtosis, skew
from dft import df_plot


df = df_helper.get_table(parameter_name="input_table", parameter_display_name="Input Table",parameter_description="Input Raw Table")
column_category = df_helper.get_string("Column Category", "Chose Column Category","Specify the column category (numeric or category)")

# CONFIGS
frac_unique_count = 0.3
number_of_class = 6
number_distinct_count = 15
min_freq_pct = 1
min_freq_count = 5


def numeric_column_stat(data):
    data = pd.DataFrame(data)
    if data.shape[1] == 1:
        stat = pd.DataFrame()
    else:
        stat = pd.DataFrame()
        stat = pd.concat([stat, data.apply('count')], axis=1)
        stat = pd.concat([stat, data.apply(lambda x: list(x.mode())).T], axis=1)
        stat = pd.concat([stat, data.apply('max')], axis=1)

        qn = [0.95, 0.75, 0.5, 0.25, 0.05]
        for i in qn:
            stat = pd.concat([stat, data.quantile(i)], axis=1)
    

        stat = pd.concat([stat, data.apply('min')], axis=1)

        stats = ['mean', 'sum', 'nunique', 'skew', 'kurtosis']
        for i in stats:
            stat = pd.concat([stat, data.apply(i)], axis=1)

        stat = pd.concat([stat, data.apply(lambda x: max(x) - min(x))], axis=1)
        stat = pd.concat([stat, data.isna().sum()], axis=1)

        stat.columns = ['VALUES', 'MOST FREQUENT', 'MAX', '95%', 'Q3', 'MEDIAN', 'Q1', '5%', 'MIN', 'AVG', 'TOTAL',
                        'DISTINCT', 'SKEWNESS', 'KURTOSIS', 'RANGE', 'MISSING']
    return stat


def category_column_stat(data):
    data = pd.DataFrame(data)
    if data.shape[1] == 1:
        most_freq = data.apply(lambda x: x.mode()).values
        most_freq = np.reshape(most_freq, len(most_freq)).tolist()
        stat = {'VALUE': data.apply('count')[0],
                'MOST FREQUENT': str(most_freq),
                'DISTINCT': data.apply('nunique')[0],
                'MISSING': data.isna().sum()[0]}
        stat = pd.DataFrame(stat,index = [data.columns])

    else:
        stat = pd.DataFrame()
        stat = pd.concat([stat, data.apply('count')], axis=1)
        stat = pd.concat([stat, data.apply(lambda x: list(x.mode())).T], axis=1)

        stat = pd.concat([stat, data.apply('nunique')], axis=1)
        stat = pd.concat([stat, data.isna().sum()], axis=1)

    
        stat.columns = ['VALUES', 'MOST FREQUENT', 'DISTINCT', 'MISSING']
    return stat


if column_category == 'Numeric':
    float_columns = list(df.select_dtypes(include=['float']).columns)
    new_columns = []
    for col in float_columns:
        table = pd.DataFrame(df[col].value_counts(bins=number_of_class, sort=False)).reset_index()
        table.columns = [col, 'Frequency']
        table[col] = table[col].astype(str)
        df_plot.bar_chart('Frequency Distribution Of ' + col, table.columns[0], table.columns[1], table)

    if len(float_columns) > 0:
        stat_table = numeric_column_stat(df[float_columns])
    else:
        stat_table = pd.DataFrame()

    int_columns = list(df.select_dtypes(include=['int']).columns)

    for col in int_columns:
        if df[col].nunique() > number_distinct_count:
            new_columns = new_columns + [col]
            table = pd.DataFrame(df[col].value_counts(bins=number_of_class, sort=False)).reset_index()
            table.columns = [col, 'Frequency']
            table[col] = table[col].astype(str)
            df_plot.bar_chart('Frequency Distribution Of ' + col, table.columns[0], table.columns[1], table)

        else:
            pass

    if len(new_columns) > 0:
        stat_table_int = numeric_column_stat(df[new_columns])

    else:
        stat_table_int = pd.DataFrame()

    stat_table = pd.concat([stat_table, stat_table_int], axis=0)

else:
    columns = list(df.select_dtypes(include=['object', 'bool']).columns)
    new_columns = []
    if len(columns) > 0:
        stat_table = category_column_stat(df[columns])
    else:
        stat_table = pd.DataFrame()
    
    int_columns = list(df.select_dtypes(include=['int']).columns)
    
    for col in int_columns:
        if df[col].nunique() < number_distinct_count:
            new_columns = new_columns + [col]
            if df[col].nunique() > min_freq_count:
                table = pd.DataFrame(df[col].value_counts()).reset_index()
                table.columns = [col, 'Count']
                df_plot.bar_chart('Frequency Distribution Of ' + col, table.columns[0], table.columns[1], table)
            else:
                table = pd.DataFrame(df[col].value_counts()).reset_index()
                table.columns = [col, 'Count']
                df_plot.pie_chart('Count For ' + col, table.columns[0], table.columns[1], table)
        else:
            pass
    if len(new_columns) > 0:
        cat_stat_table = category_column_stat(df[new_columns])
    else:
        cat_stat_table = pd.DataFrame()
    for col in columns:
        if df[col].nunique() / len(df[col]) < frac_unique_count:
            if df[col].nunique() > number_distinct_count:
                series = pd.value_counts(df[col])
                mask = (series / series.sum() * 100).lt(min_freq_pct)
                # To replace df['column'] use np.where I.e
                df[col] = np.where(df[col].isin(series[mask].index), 'Other', df[col])
                new = series[~mask]
                new['Other'] = series[mask].sum()
                table = pd.DataFrame(new).reset_index()
                df_plot.bar_chart('Frequency Distribution Of ' + col, table.columns[0], table.columns[1], table)
            else:
                if df[col].nunique() <= min_freq_count:
                    table = pd.DataFrame(df[col].value_counts()).reset_index()
                    table.columns = [col, 'Count']
                    df_plot.bar_chart('Frequency Distribution Of ' + col, table.columns[0], table.columns[1], table)
                else:
                    table = pd.DataFrame(df[col].value_counts()).reset_index()
                    table.columns = [col, 'Count']
                    df_plot.pie_chart('Count For ' + col, table.columns[0], table.columns[1], table)
        else:
            pass
    stat_table = pd.concat([stat_table, cat_stat_table], axis=0)

#

df_helper.publish(stat_table.reset_index())