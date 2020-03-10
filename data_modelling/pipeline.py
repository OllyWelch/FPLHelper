from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from data_modelling.data_fetcher import DataFetcher
from data_modelling.pre_scaler import PreScaler
from utils import timer
import joblib
import os


@timer
def pipeline(manual_engine=None):
    """Executes the data pipeline: fetches data using DataFetcher class, trains and fits the model to
    the next gameweek's data. Also uses the opportunity to fetch the next gameweek number from the db.
    Manual db engine option supplied for when working outside of application context."""

    # Fetch data from database: we have labelled training data and unlabelled prediction data
    data_fetcher = DataFetcher(manual_engine=manual_engine)
    training_data = data_fetcher.get_training_data()
    next_gameweek = data_fetcher.get_next_gameweek()

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

    # fit the model to the training data

    pipe.fit(X, y)

    # save the model and next gameweek to disk

    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    model_filename = 'data/finalized_model.pkl'
    with open(os.path.abspath(os.path.join(base, model_filename)), 'wb') as f:
        joblib.dump(pipe, f)

    next_gameweek_filename = 'data/next_gameweek.sav'
    with open(os.path.abspath(os.path.join(base, next_gameweek_filename)), 'wb') as f:
        joblib.dump(next_gameweek, f)