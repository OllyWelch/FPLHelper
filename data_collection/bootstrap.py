import requests
import pandas as pd
import numpy as np
import data_collection.util as util
import json


class Bootstrap:

    def __init__(self):
        self.bootstrap = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/").json()
        self.team_data = self.get_team_data()
        self.team_ids = self.team_data.reindex(columns=['id', 'name', 'short_name'])
        self.players_data = self.get_players_data()
        self.events = pd.read_json(json.dumps(self.bootstrap['events'])).reindex(
            columns=['id', 'deadline_time', 'finished'])
        self.next_event = self.events[self.events.finished == False].id.values[0]

    def get_team_data(self):
        teams = self.bootstrap['teams']
        columnkeys = list(teams[0].keys())
        teamdata = np.array([[d[columnkey] for columnkey in columnkeys] for d in teams])
        return util.dfcolumnstonumeric(pd.DataFrame(teamdata, columns=columnkeys))

    def get_team_name(self, teamid):
        try:
            return self.team_ids['name'][self.team_ids.id == teamid].values[0]
        except IndexError:
            print('Invalid team code entered')

    def get_team_id(self, teamname):
        try:
            return self.team_ids['id'][self.team_ids.name == teamname].values[0]
        except IndexError:
            print('Invalid team name entered')

    def get_players_data(self):
        players = self.bootstrap['elements']
        columnkeys = list(players[0].keys())
        playerdata = np.array([[d[columnkey] for columnkey in columnkeys] for d in players])
        return util.dfcolumnstonumeric(pd.DataFrame(playerdata, columns=columnkeys))

    def get_player_info(self, player_id, columns=None, team_code_as_name=False):
        if columns is None:
            data = self.players_data[self.players_data.id == player_id]
        else:
            try:
                data = self.players_data[self.players_data.id == player_id][columns]
            except KeyError:
                print('Error: invalid columns specified')
                return None
        if team_code_as_name:
            try:
                data['team_name'] = str(self.get_team_name(data['team'].values[0]))
                data = data.drop(columns='team', axis=1)
                return data
            except KeyError:
                return 'Error: team code not a specified column'
        return data

    def get_player_id(self, second_name, first_name=None, team_name=None):
        secondname = self.players_data.second_name == second_name
        if first_name is not None:
            firstname = self.players_data.first_name == first_name
            if team_name is not None:
                team_id = self.get_team_id(team_name)
                teamid = self.players_data.team == team_id
                return self.players_data['id'][firstname & secondname & teamid].values[0]
            return self.players_data['id'][firstname & secondname].values[0]
        else:
            if team_name is not None:
                team_id = self.get_team_id(team_name)
                teamid = self.players_data.team == team_id
                return self.players_data['id'][secondname & teamid].values[0]
        return self.players_data['id'][secondname].values[0]

    def get_event_statuses(self):
        return self.events
