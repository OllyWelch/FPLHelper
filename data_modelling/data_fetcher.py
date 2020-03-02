import data_collection.util as util
import pickle
import os


class DataFetcher:

    def __init__(self, team_predict=False):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.features = pickle.load(open(os.path.abspath(os.path.join(base, 'data/features.sav')), 'rb'))
        self.response = pickle.load(open(os.path.abspath(os.path.join(base, 'data/response.sav')), 'rb'))
        if not team_predict:
            training_data = self.features[self.features.time < max(self.features.time)].join(self.response, on='entry_id').drop(columns=['time'])
            prediction_data = self.features[self.features.time == max(self.features.time)].drop(columns=['time'])
            self.training_data = util.was_home_to_numeric(training_data)
            self.prediction_data = util.was_home_to_numeric(prediction_data)
        self.player_names = pickle.load(open(os.path.abspath(os.path.join(base, 'data/player_names.sav')), 'rb'))
        self.event_statuses = pickle.load(open(os.path.abspath(os.path.join(base, 'data/event_statuses.sav')), 'rb')).set_index('id')
        next_unfinished_gameweek = int(self.event_statuses[self.event_statuses.finished == False].index[0])
        last_db_update = max(self.features.time)
        last_finished_gameweek_deadline = max(self.event_statuses[self.event_statuses.finished == True].loc[:, 'deadline_time'])
        self.next_gameweek = next_unfinished_gameweek if last_db_update > last_finished_gameweek_deadline \
            else next_unfinished_gameweek - 1
        self.initial_prices = pickle.load(open(os.path.abspath(os.path.join(base, 'data/initial_prices.sav')), 'rb'))
