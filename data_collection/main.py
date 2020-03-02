import pandas as pd
import numpy as np
import pickle
import datetime
from data_collection.util import dfcolumnstonumeric
from data_collection.bootstrap import Bootstrap
from data_collection.player import Player
from utils import timer
import os


class Main:

    def __init__(self):
        self.base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.features = pickle.load(open(os.path.abspath(os.path.join(self.base, 'data/features.sav')), 'rb'))
        self.bootstrap = Bootstrap()
        self.player_ids = self.bootstrap.players_data['id'].values
        self.prev_player_ids = self.features[self.features.time == max(self.features.time)]['id'].values
        self.prev_entry_ids = self.features[self.features.time == max(self.features.time)].index.values
        self.n_players = len(self.player_ids)
        self.n_prev_players = len(self.prev_player_ids)
        self.n_entries = len(self.prev_entry_ids)
        self.new_entry_ids = range(self.prev_entry_ids[-1] + 1, self.prev_entry_ids[-1] + self.n_players + 1)
        self.player_positions = {
            '1': 'GKP',
            '2': 'DEF',
            '3': 'MID',
            '4': 'FWD'
        }
        self.counter = 0

    def get_feature_vector(self, player_id):
        player = Player(player_id)
        a = player.get_player_team_stats()
        b = player.get_next_fixture_data()
        c = player.get_player_last_three()
        d = player.get_player_overall()
        feature_vector = pd.concat([d, c, a, b], axis=1).fillna(method='ffill')
        feature_vector['n_games'] = len(feature_vector.index) if feature_vector.opposition.values[0] != 0 else 0
        self.counter += 1
        print('{}% complete'.format(round((self.counter / len(self.player_ids) * 100), 2)))
        return pd.DataFrame(feature_vector.mean(axis=0)).transpose()

    @timer
    def get_features(self, new):
        feature_vectors = [self.get_feature_vector(int(player_id)) for player_id in self.player_ids]
        data = pd.concat(feature_vectors, sort=False)
        data['time'] = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        data['time'] = pd.to_datetime(data['time'])
        data['entry_id'] = self.new_entry_ids if new else range(self.prev_entry_ids[0], self.prev_entry_ids[0] + len(data.index))
        return data.set_index('entry_id')

    def get_player_response(self, player_id):
        print(player_id)
        player = Player(player_id, bootstrap=False)
        n_games = int(self.features[
            (self.features.time == max(self.features.time)) & (self.features.id == player_id)]['n_games'].values[0])
        try:
            point = player.get_player_last_game(n_games)
        except KeyError:
            point = 0
        return point

    @timer
    def get_response(self):
        responses = [self.get_player_response(int(player_id)) for player_id in self.prev_player_ids]
        indices = self.prev_entry_ids
        return pd.DataFrame({'entry_id': indices, 'points': responses}).set_index('entry_id')

    def gameweek_finished(self):
        gameweeks = self.bootstrap.get_event_statuses()
        truth_value = gameweeks[gameweeks.deadline_time <
                                '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())].iloc[-1, 2]
        return truth_value

    def last_gameweek_response_added(self):
        gameweeks = self.bootstrap.get_event_statuses()
        most_recent_gameweek = gameweeks[gameweeks.deadline_time <
                                         '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())].iloc[-1, 1]
        most_recent_update = max(self.features.time)
        return most_recent_update < most_recent_gameweek

    def updated_player_name_position(self, player_id):
        player_name = self.bootstrap.get_player_info(
            player_id, columns=['first_name', 'second_name', 'element_type', 'now_cost', 'team']).values.tolist()[0]
        return player_name

    @timer
    def update_player_names(self):
        player_names = [self.updated_player_name_position(player_id) for player_id in self.player_ids]
        player_names = np.array(player_names)
        player_names_df = pd.DataFrame({'id': self.player_ids, 'first_name': player_names[:, 0],
                                        'second_name': player_names[:, 1], 'position': player_names[:, 2],
                                        'price': player_names[:, 3], 'team': player_names[:, 4]})
        player_names_df['position'] = player_names_df['position'].map(self.player_positions)
        player_names_df['price'] = player_names_df['price'].astype(int) / 10
        player_names_df = dfcolumnstonumeric(player_names_df)
        pickle.dump(player_names_df, open(os.path.abspath(os.path.join(self.base, 'data/player_names.sav')), 'wb'))

    def get_player_initial_price(self, player_id):
        player = Player(player_id, bootstrap=False)
        try:
            return player.get_player_history().loc[0, 'value']/10
        except KeyError:
            return np.nan

    @timer
    def update_initial_prices(self):
        prices = [self.get_player_initial_price(player_id) for player_id in self.player_ids]
        initial_prices = pd.DataFrame({'id': self.player_ids, 'price': prices})
        pickle.dump(initial_prices, open(os.path.abspath(os.path.join(self.base, 'data/initial_prices.sav')), 'wb'))

    @timer
    def update_event_statuses(self):
        event_statuses = self.bootstrap.get_event_statuses()
        pickle.dump(event_statuses, open(os.path.abspath(os.path.join(self.base, 'data/event_statuses.sav')), 'wb'))
