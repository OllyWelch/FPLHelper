import pickle
from data_collection.bootstrap import Bootstrap
import os


def get_predictions():
    """Function for retrieving serialized model prediction data as well as the next gameweek"""

    # Set base directory and retrieve serialized predictions/next_gameweek files
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    filename_predictions = 'data/predictions.sav'
    filename_next_gameweek = 'data/next_gameweek.sav'
    predictions = pickle.load(open(os.path.abspath(os.path.join(base, filename_predictions)), 'rb'))
    next_gameweek = pickle.load(open(os.path.abspath(os.path.join(base, filename_next_gameweek)), 'rb'))

    # Add team names to predictions through access to Bootstrap Static API
    bootstrap = Bootstrap()
    predictions = predictions.join(bootstrap.team_ids.set_index('id'), on='team').reindex(
        columns=['position', 'first_name', 'second_name', 'price', 'short_name', 'expected_points', 'value']).rename(
        columns={'short_name': 'team'})

    return {
        'next_gameweek': next_gameweek,
        'predictions': predictions
    }
