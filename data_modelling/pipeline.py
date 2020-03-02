from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from data_modelling.data_fetcher import DataFetcher
from data_modelling.pre_scaler import PreScaler
import joblib
import os


def pipeline():
    # Fetch data from database: we have labelled training data and unlabelled prediction data
    data_fetcher = DataFetcher()
    training_data = data_fetcher.training_data

    # Split into train and test sets of features and response
    X, y = training_data.drop(columns=['points']).reset_index(drop=True), training_data['points']
    X = X.set_index('id')

    # DATA PIPELINE:

    pipe = Pipeline([
        ('pre_scaler', PreScaler()),
        ('imputer', SimpleImputer()),
        ('scaler', StandardScaler()),
        ('regressor', RandomForestRegressor(n_estimators=100, max_depth=20, max_features=20, min_samples_leaf=6, random_state=0))
    ])

    pipe.fit(X, y)

    # save the model to disk
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    filename = 'data/finalized_model.pkl'
    with open(os.path.abspath(os.path.join(base, filename)), 'wb') as f:
        joblib.dump(pipe, f)
