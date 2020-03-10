import requests
import numpy as np
import pandas as pd


class Team:

    """Class which retrieves information about a given team"""

    def __init__(self, team_id, previous_gameweek, custom_transfers, name_only=False):
        self.team_id = team_id
        self.previous_gameweek = previous_gameweek
        self.custom_transfers = custom_transfers

    def get_info(self):
        return requests.get(
            "https://fantasy.premierleague.com/api/entry/{}/".format(
                self.team_id)).json()

    def get_name(self):
        team_info = requests.get(
            "https://fantasy.premierleague.com/api/entry/{}/".format(
                self.team_id)).json()
        try:
            return team_info['name']
        except:
            raise ValueError

    def get_picks(self):
        team_picks = requests.get(
            "https://fantasy.premierleague.com/api/entry/{}/event/{}/picks/".format(
                self.team_id, self.previous_gameweek)).json()
        if team_picks['active_chip'] == "freehit":
            team_picks = requests.get(
                "https://fantasy.premierleague.com/api/entry/{}/event/{}/picks/".format(
                    self.team_id, self.previous_gameweek - 1)).json()
        picks = np.array([d['element'] for d in team_picks['picks']])
        for elem in self.custom_transfers:
            mp = np.arange(0, 1000)
            mp[elem[0]] = elem[1]
            picks = mp[picks]
        return picks

    def get_transfers_in_cost(self):
        transfers = requests.get(
            "https://fantasy.premierleague.com/api/entry/{}/transfers/".format(
                self.team_id)).json()
        transfers_in_data = np.array([[entry['element_in'], entry['element_in_cost'] / 10] for entry in transfers])
        return pd.DataFrame(
            transfers_in_data, columns=['id', 'PP']).astype({'id': 'int64'}).drop_duplicates('id').set_index('id')
