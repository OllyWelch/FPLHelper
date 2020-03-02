from data_collection.main import Main
from data_modelling.pipeline import pipeline
from data_modelling.predictions_update import predictions_update
from data_modelling.data_fetcher import DataFetcher
from utils import timer
import pandas as pd
import pickle
import os


@timer
def update_data():
    # find the root directory so we can dump updated data to the data folder
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # fetch features and response from files
    data_fetcher = DataFetcher()
    features = data_fetcher.features
    response = data_fetcher.response
    # initialise main class
    main = Main()
    # update event statuses
    main.update_event_statuses()
    # update player names
    main.update_player_names()
    # update initial prices of players
    main.update_initial_prices()
    # check if the data from the last gameweek is up to date
    print('Checking if last gameweek data is complete...')
    if main.last_gameweek_response_added():
        print('Last gameweek data not complete.')
        # check if most recent gameweek is finished
        print('Checking gameweek finished...')
        if main.gameweek_finished():
            print('Gameweek finished, proceeding to update data.')
            # get response
            new_responses = main.get_response()
            new_responses = pd.concat([response, new_responses])
            pickle.dump(new_responses, open(os.path.abspath(os.path.join(base, 'data/response.sav')), 'wb'))
            print("Response successfully updated.")
            # get features
            new_features = main.get_features(new=True)
            new_features = pd.concat([features, new_features], sort=False)
            pickle.dump(new_features, open(os.path.abspath(os.path.join(base, 'data/features.sav')), 'wb'))
            print("Features successfully updated.")
        else:
            print('Gameweek currently active - no data update performed')
    else:
        # data is added from last gameweek, in this case we update the features
        if main.gameweek_finished():
            print('Last gameweek data complete, getting updated features...')
            # retrieve up to date features
            new_features = main.get_features(new=False)
            print('Updated features retrieved, deleting out of date features...')
            # remove the latest features and replace with up to date ones
            features = features[features.time < max(features.time)]
            print('Adding new features...')
            new_features = pd.concat([features, new_features], sort=False)
            pickle.dump(new_features, open(os.path.abspath(os.path.join(base, 'data/features.sav')), 'wb'))
            print('Data up to date!')
        else:
            print('Next gameweek started, no update done.')


@timer
def update_predictions():
    # update the model
    pipeline()
    # update the predictions based on the updated model
    predictions_update()
