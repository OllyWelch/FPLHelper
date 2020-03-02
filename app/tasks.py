from data_collection.main import Main
from data_modelling.pipeline import pipeline
from data_modelling.predictions_update import predictions_update
from data_modelling.data_fetcher import DataFetcher
import pandas as pd
import pickle
import os


def update_data():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_fetcher = DataFetcher()
    features = data_fetcher.features
    response = data_fetcher.response
    main = Main()
    print('Updating event statuses...')
    main.update_event_statuses()
    print('Event statuses updated.')
    print('Updating player names...')
    player_names = [main.updated_player_name_position(player_id) for player_id in main.player_ids]
    main.update_player_names(player_names)
    print('Player names updated.')
    print('Getting initial prices...')
    main.add_initial_prices()
    print('Initial prices updated.')
    print('Checking if last gameweek data is complete...')
    if main.last_gameweek_response_added():
        print('Last gameweek data not complete.')
        # check if most recent gameweek is finished
        print('Checking gameweek finished...')
        if main.gameweek_finished():
            print('Gameweek finished, proceeding to update data.')
            # get response
            print("Getting response... \n")
            responses = [main.get_player_response(int(player_id)) for player_id in main.prev_player_ids]
            new_response = pd.concat([response, main.get_response(responses)])
            pickle.dump(new_response, open(os.path.abspath(os.path.join(base, 'data/response.sav')), 'wb'))
            print("Response successfully updated. \n")
            # get features
            print("Getting features...")
            # features = get_features()
            feature_vectors = [main.get_feature_vector(int(player_id)) for player_id in main.player_ids]
            new_features = pd.concat([features, main.get_features(feature_vectors, new=True)], sort=False)
            pickle.dump(new_features, open(os.path.abspath(os.path.join(base, 'data/features.sav')), 'wb'))
            print("Features successfully updated.")
        else:
            print('Gameweek currently active - no database update performed')
    else:
        if main.gameweek_finished():
            print('Last gameweek data complete, getting updated features...')
            feature_vectors = [main.get_feature_vector(int(player_id)) for player_id in main.player_ids]
            new_features = main.get_features(feature_vectors, new=False)
            print('Updated features retrieved, deleting out of date features...')
            features = features[features.time < max(features.time)]
            print('Adding new features...')
            new_features = pd.concat([features, new_features], sort=False)
            pickle.dump(new_features, open(os.path.abspath(os.path.join(base, 'data/features.sav')), 'wb'))
            print('Data up to date!')
        else:
            print('Next gameweek started, no update done.')


def update_predictions():
    print('Updating model...')
    pipeline()
    print('Model updated.')
    print('Updating predictions...')
    predictions_update()
    print('Predictions updated.')
