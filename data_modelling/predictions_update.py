import pandas as pd
import pickle
import joblib
from data_modelling.data_fetcher import DataFetcher
from utils import timer
import os


@timer
def predictions_update():
    # Fetch data from database: we have labelled training data and unlabelled prediction data
    data_fetcher = DataFetcher()
    prediction_data = data_fetcher.prediction_data
    player_names = data_fetcher.player_names.set_index('id')

    # Load the saved model
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    filename = 'data/finalized_model.pkl'
    grid = joblib.load(os.path.abspath(os.path.join(base, filename)))

    # Predict each players XP, and replace their id with their name
    X_predict = prediction_data.reset_index(drop=True).set_index('id')
    predictions = grid.predict(X_predict)
    predictions = pd.DataFrame({'id': X_predict.index,
                                'expected_points': predictions}).join(player_names, on='id').sort_values(
        'expected_points', ascending=False).set_index('id')
    predictions = predictions.join(data_fetcher.initial_prices.rename(columns={'price': 'initial_price'}).set_index('id'), on='id')
    predictions = predictions.reindex(
        columns=['position', 'first_name', 'second_name', 'price', 'initial_price', 'team', 'expected_points'])
    predictions['value'] = predictions['expected_points']/predictions['price']
    predictions = predictions.round({'expected_points': 2, 'value': 2})
    filename = 'data/predictions.sav'
    with open(os.path.abspath(os.path.join(base, filename)), 'wb') as f:
        pickle.dump(predictions, f)

