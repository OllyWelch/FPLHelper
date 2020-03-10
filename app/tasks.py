from data_collection.main import Main
from data_modelling.pipeline import pipeline
from data_modelling.predictions_update import predictions_update
from data_modelling.data_fetcher import DataFetcher
import sqlalchemy as db
from utils import timer
import pandas as pd
import os
from dotenv import load_dotenv

# Find the root directory and load environment variables from .env file
base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(base, '.env'))

# Create database connection through the DB URL in the .env file
manual_engine = db.create_engine(os.environ.get('FPL_DATABASE_URL'))


@timer
def update_data():
    """Accesses the FPL API and updates all database tables"""

    # fetch features and response from files
    data_fetcher = DataFetcher(manual_engine=manual_engine)
    features = data_fetcher.get_features()
    response = data_fetcher.get_response()

    # initialise main class
    main = Main(manual_engine=manual_engine)

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
            new_responses.to_sql('response', manual_engine, if_exists='replace')
            print("Response successfully updated.")

            # get features
            new_features = main.get_features(new=True)
            new_features = pd.concat([features, new_features], sort=False)
            new_features.to_sql('features', manual_engine, if_exists='replace')
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
            new_features.to_sql('features', manual_engine, if_exists='replace')
            print('Data up to date!')
        else:
            print('Next gameweek started, no update done.')


@timer
def update_predictions():
    """Updates the model based on the updated data, and then updates the
    predictions based on the updated model"""

    # update the model
    pipeline(manual_engine=manual_engine)

    # update the predictions based on the updated model
    predictions_update(manual_engine=manual_engine)
