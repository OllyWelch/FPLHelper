import requests
import numpy as np
import pandas as pd


class Team:

    def __init__(self, team_id, previous_gameweek, custom_transfers, name_only=False):
        self.team_id = team_id
        self.previous_gameweek = previous_gameweek
        if not name_only:
            self.team_picks = requests.get(
                "https://fantasy.premierleague.com/api/entry/{}/event/{}/picks/".format(
                    self.team_id, self.previous_gameweek)).json()
            if self.team_picks['active_chip'] == "freehit":
                self.team_picks = requests.get(
                "https://fantasy.premierleague.com/api/entry/{}/event/{}/picks/".format(
                    self.team_id, self.previous_gameweek - 1)).json()
            self.picks = np.array([d['element'] for d in self.team_picks['picks']])
            for elem in custom_transfers:
                mp = np.arange(0, 1000)
                mp[elem[0]] = elem[1]
                self.picks = mp[self.picks]
            transfers = requests.get(
                "https://fantasy.premierleague.com/api/entry/{}/transfers/".format(
                    self.team_id)).json()
            transfers_in_data = np.array([[entry['element_in'], entry['element_in_cost'] / 10] for entry in transfers])
            self.transfers_in_cost = pd.DataFrame(
                transfers_in_data, columns=['id', 'PP']).astype({'id': 'int64'}).drop_duplicates('id').set_index('id')
        self.team_info = requests.get(
            "https://fantasy.premierleague.com/api/entry/{}/".format(
                self.team_id)).json()
        try:
            self.team_name = self.team_info['name']
        except:
            raise ValueError

