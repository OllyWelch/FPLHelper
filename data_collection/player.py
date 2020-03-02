import requests
import pandas as pd
import numpy as np
import data_collection.util as util
from data_collection.bootstrap import Bootstrap


class Player:

    def __init__(self, player_id, bootstrap=True):
        self.player_id = player_id
        self.player_data = requests.get(
            "https://fantasy.premierleague.com/api/element-summary/{}/".format(self.player_id)).json()
        self.player_positions = {
            1: 'GKP',
            2: 'DEF',
            3: 'MID',
            4: 'FWD'
        }
        if bootstrap:
            self.bootstrap = Bootstrap()

    def get_player_history(self):
        try:
            player_history = self.player_data['history']
            try:
                columnlist = list(player_history[0].keys())
                data = np.array([[d[column] for column in columnlist] for d in player_history])
                return util.dfcolumnstonumeric(pd.DataFrame(data, columns=columnlist))
            except IndexError:
                return pd.DataFrame(np.zeros([1, 20]), columns=['total_points', 'opponent_team', 'was_home', 'minutes',
                                                              'goals_scored', 'assists', 'clean_sheets',
                                                              'goals_conceded',
                                                              'own_goals', 'penalties_saved', 'penalties_missed',
                                                              'yellow_cards',
                                                              'red_cards', 'saves', 'bonus', 'bps', 'influence',
                                                              'creativity',
                                                              'threat', 'ict_index'])
        except KeyError:
            return pd.DataFrame(np.zeros([1, 20]), columns=['total_points', 'opponent_team', 'was_home', 'minutes',
                                                       'goals_scored', 'assists', 'clean_sheets', 'goals_conceded',
                                                       'own_goals', 'penalties_saved', 'penalties_missed',
                                                       'yellow_cards',
                                                       'red_cards', 'saves', 'bonus', 'bps', 'influence', 'creativity',
                                                       'threat', 'ict_index'])

    def get_player_last_game(self, n_games):
        try:
            player_history = self.player_data['history']
            try:
                if n_games > 0:
                    return sum(pd.DataFrame(player_history[-n_games:])['total_points'])
                return 0
            except IndexError:
                return 0
        except KeyError:
            return 0

    def get_player_fixtures(self):
        player_fixtures = self.player_data['fixtures']
        columnlist = list(player_fixtures[0].keys())
        n_columns = len(columnlist)
        data = np.array([[d[column] for column in columnlist] if len(d) == n_columns else [0 for i in range(n_columns)]
                         for d in player_fixtures])
        return util.dfcolumnstonumeric(pd.DataFrame(data, columns=columnlist))

    def get_player_last_three(self):
        player_history = self.get_player_history()
        columnlist = ['total_points', 'opponent_team', 'was_home', 'minutes',
                      'goals_scored', 'assists', 'clean_sheets', 'goals_conceded',
                      'own_goals', 'penalties_saved', 'penalties_missed', 'yellow_cards',
                      'red_cards', 'saves', 'bonus', 'bps', 'influence', 'creativity',
                      'threat', 'ict_index']
        player_history = player_history.reindex(columns=columnlist)
        flattened_last_three = np.array(player_history.iloc[-3:, :]).flatten()
        missing_vals = 60 - len(flattened_last_three)
        filler = np.full((1, missing_vals), np.nan)
        flattened_last_three = np.append(filler, flattened_last_three)
        new_column_list = ['total_points_3', 'opponent_team_3', 'was_home_3', 'minutes_3',
                           'goals_scored_3', 'assists_3', 'clean_sheets_3', 'goals_conceded_3',
                           'own_goals_3', 'penalties_saved_3', 'penalties_missed_3', 'yellow_cards_3',
                           'red_cards_3', 'saves_3', 'bonus_3', 'bps_3', 'influence_3', 'creativity_3',
                           'threat_3', 'ict_index_3', 'total_points_2', 'opponent_team_2', 'was_home_2', 'minutes_2',
                           'goals_scored_2', 'assists_2', 'clean_sheets_2', 'goals_conceded_2',
                           'own_goals_2', 'penalties_saved_2', 'penalties_missed_2', 'yellow_cards_2',
                           'red_cards_2', 'saves_2', 'bonus_2', 'bps_2', 'influence_2', 'creativity_2',
                           'threat_2', 'ict_index_2', 'total_points_1', 'opponent_team_1', 'was_home_1', 'minutes_1',
                           'goals_scored_1', 'assists_1', 'clean_sheets_1', 'goals_conceded_1',
                           'own_goals_1', 'penalties_saved_1', 'penalties_missed_1', 'yellow_cards_1',
                           'red_cards_1', 'saves_1', 'bonus_1', 'bps_1', 'influence_1', 'creativity_1',
                           'threat_1', 'ict_index_1']
        return pd.DataFrame([flattened_last_three], columns=new_column_list).reset_index(drop=True)

    def get_next_fixture_data(self):
        next_fixture_cols = ['team_h', 'team_a', 'is_home', 'difficulty']
        next_fixtures = self.get_player_fixtures()
        next_gameweek_fixtures = next_fixtures[next_fixtures.event == self.bootstrap.next_event]
        if len(next_gameweek_fixtures.index) == 0:
            return pd.DataFrame(np.zeros(6), index=['opposition', 'is_home', 'opposition_strength', 'opposition_overall',
                                                         'opposition_attack', 'opposition_defence']).transpose()
        next_fixtures = next_gameweek_fixtures.reindex(columns=next_fixture_cols)
        next_fixtures['id'] = [next_fixtures['team_a'][i] if next_fixtures['is_home'][i] else next_fixtures['team_h'][i]
                               for i in range(len(next_fixtures.index))]
        next_fixtures = next_fixtures.reindex(columns=['id', 'is_home', 'difficulty'])
        team_data = self.bootstrap.team_data
        team_data = team_data.reindex(
            columns=['id', 'strength', 'strength_overall_home', 'strength_overall_away',
                     'strength_attack_home', 'strength_attack_away', 'strength_defence_home',
                     'strength_defence_away'])
        next_fixtures_data = next_fixtures.join(team_data.set_index('id'), on='id')
        next_fixtures_data['opposition_overall'] = [next_fixtures_data['strength_overall_away'][i] if
                                                    next_fixtures['is_home'][i] else
                                                    next_fixtures_data['strength_overall_home'][i] for i in
                                                    range(len(next_fixtures_data.index))]
        next_fixtures_data['opposition_attack'] = [next_fixtures_data['strength_attack_away'][i] if
                                                   next_fixtures['is_home'][i] else
                                                   next_fixtures_data['strength_attack_home'][i] for i in
                                                   range(len(next_fixtures_data.index))]
        next_fixtures_data['opposition_defence'] = [next_fixtures_data['strength_defence_away'][i] if
                                                    next_fixtures['is_home'][i] else
                                                    next_fixtures_data['strength_defence_home'][i] for i in
                                                    range(len(next_fixtures_data.index))]
        next_fixtures_data = next_fixtures_data.reindex(columns=['id', 'is_home', 'strength',
                                                                 'opposition_overall', 'opposition_attack',
                                                                 'opposition_defence'])
        next_fixtures_data = next_fixtures_data.rename(columns={'id': 'opposition', 'strength': 'opposition_strength'})
        return next_fixtures_data.reset_index(drop=True)

    def get_player_overall(self):
        return self.bootstrap.get_player_info(self.player_id, ['id', 'element_type', 'chance_of_playing_next_round',
                                                            'chance_of_playing_this_round',
                                                            'form', 'points_per_game', 'total_points', 'minutes',
                                                            'goals_scored',
                                                            'assists', 'clean_sheets', 'goals_conceded', 'own_goals',
                                                            'penalties_saved', 'penalties_missed', 'yellow_cards',
                                                            'red_cards',
                                                            'saves', 'bonus', 'bps', 'influence', 'creativity',
                                                            'threat',
                                                            'ict_index']).reset_index(drop=True)

    def get_player_team_stats(self):
        player_team_id = self.bootstrap.get_player_info(self.player_id, columns=['team']).values[0][0]
        teamdata = self.bootstrap.team_data
        return teamdata[teamdata.id == player_team_id].reindex(
            columns=['strength', 'strength_overall_home', 'strength_overall_away',
                     'strength_attack_home', 'strength_attack_away', 'strength_defence_home',
                     'strength_defence_away']).reset_index(drop=True)
