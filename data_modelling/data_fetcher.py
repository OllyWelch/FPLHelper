from flask import current_app
import data_collection.util as util
from data_collection.bootstrap import Bootstrap
import pandas as pd


class DataFetcher:

    """Allows the retrieval of data from the fpldb database on RDS. Each
    get function retrieves a specific table while setting its value as an attribute"""

    def __init__(self, manual_engine=None):
        self.engine = current_app.engine if manual_engine is None else manual_engine
        self.features = None
        self.response = None
        self.event_statuses = None
        self.next_gameweek = None

    def get_data(self, table_name, index=None):
        # Generic method for retrieving data from a table in a Pandas Dataframe
        columns = [value for value, in list(
            self.engine.execute('SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = \'{}\' '.format(
                table_name)))]
        data = pd.DataFrame(self.engine.execute('SELECT * FROM {}'.format(table_name)), columns=columns)
        if index is not None:
            data = data.set_index(index)
        return data

    def get_features(self):
        self.features = self.get_data('features', index='entry_id')
        return self.features

    def get_response(self):
        self.response = self.get_data('response', index='entry_id')
        return self.response

    # Methods for getting training/prediction data for the ML
    def get_training_data(self):
        features = self.get_features() if self.features is None else self.features
        response = self.get_response() if self.response is None else self.response
        training_data = features[features.time < max(features.time)].join(response, on='entry_id').drop(
            columns=['time'])
        return util.was_home_to_numeric(training_data)

    def get_prediction_data(self):
        features = self.get_features() if self.features is None else self.features
        prediction_data = features[features.time == max(features.time)].drop(columns=['time'])
        return util.was_home_to_numeric(prediction_data)

    # Methods for retrieving general info about gameweeks, player names etc.
    def get_player_names(self):
        return self.get_data('player_names', index='index')

    def get_event_statuses(self):
        self.event_statuses = self.get_data('event_statuses', index='id')
        return self.event_statuses

    def get_initial_prices(self):
        return self.get_data('initial_prices', index='index')

    def get_next_gameweek(self):
        event_statuses = self.get_event_statuses() if self.event_statuses is None else self.event_statuses
        features = self.get_features() if self.features is None else self.features
        next_unfinished_gameweek = int(event_statuses[event_statuses.finished == False].index[0])
        last_db_update = max(features.time)
        last_finished_gameweek_deadline = max(
            event_statuses[event_statuses.finished == True].loc[:, 'deadline_time'])
        next_gameweek = next_unfinished_gameweek if last_db_update > last_finished_gameweek_deadline \
            else next_unfinished_gameweek - 1
        self.next_gameweek = next_gameweek
        return self.next_gameweek
