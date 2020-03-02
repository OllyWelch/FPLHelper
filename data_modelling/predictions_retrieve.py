import pickle
from data_collection.bootstrap import Bootstrap
from data_modelling.data_fetcher import DataFetcher
import os


def get_predictions():
    data_fetcher = DataFetcher()
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    filename = 'data/predictions.sav'
    predictions = pickle.load(open(os.path.abspath(os.path.join(base, filename)), 'rb'))
    # Show the top n players by position and overall
    bootstrap = Bootstrap()
    predictions = predictions.join(bootstrap.team_ids.set_index('id'), on='team').reindex(
        columns=['position', 'first_name', 'second_name', 'price', 'short_name', 'expected_points', 'value']).rename(
        columns={'short_name': 'team'})
    next_gameweek = data_fetcher.next_gameweek
    result = {
        'next_gameweek': next_gameweek,
        'predictions': predictions
    }
    return result
