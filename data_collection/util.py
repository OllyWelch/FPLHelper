import pandas as pd


def dfcolumnstonumeric(df):
    # where possible, convert dtypes of each column to numeric type
    for i in range(len(df.columns)):
        df.iloc[:, i] = pd.to_numeric(df.iloc[:, i], errors='ignore')
    return df


def was_home_to_numeric(df):
    # Map each 'was home' column boolean value to an int64/None type
    categorical_columns = ['was_home_{}'.format(i) for i in [1, 2, 3]]
    for column in categorical_columns:
        df[column] = df[column].map({'True': 1, 'False': 0, 'None': None})
    return df
