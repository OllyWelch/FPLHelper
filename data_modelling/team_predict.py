import pickle
from data_modelling.team import Team
from data_modelling.data_fetcher import DataFetcher
import numpy as np
import os


def get_best_position_comb(team_predictions, formation, position):
    return team_predictions[
               team_predictions.position == position].sort_values(
        'expected_points', ascending=False).reset_index().loc[:formation[position]-1, 'id'].values


def get_best_formation_comb(team_predictions, formation):
    return np.concatenate(np.array(
        list(map(get_best_position_comb, [team_predictions]*len(formation), [formation]*len(formation), formation))))


def find_best_combination(team_predictions):
    best_formation_combs = np.array([{
        'GKP': 1,
        'DEF': 3,
        'MID': 4,
        'FWD': 3
    }, {
        'GKP': 1,
        'DEF': 3,
        'MID': 5,
        'FWD': 2
    }, {
        'GKP': 1,
        'DEF': 4,
        'MID': 5,
        'FWD': 1
    }, {
        'GKP': 1,
        'DEF': 4,
        'MID': 4,
        'FWD': 2
    }, {
        'GKP': 1,
        'DEF': 4,
        'MID': 3,
        'FWD': 3
    }, {
        'GKP': 1,
        'DEF': 5,
        'MID': 4,
        'FWD': 1
    }, {
        'GKP': 1,
        'DEF': 5,
        'MID': 3,
        'FWD': 2
    }])
    # Find best team and their corresponding expected score
    best_formation_combs = np.array(list(map(get_best_formation_comb, [team_predictions]*len(best_formation_combs), best_formation_combs)))
    best_scores = np.array(list(map(
        lambda team_prediction, selection: sum(team_prediction.loc[selection, 'expected_points']),
        [team_predictions]*len(best_formation_combs), best_formation_combs)))
    best_score, best_team = np.amax(best_scores), best_formation_combs[np.argmax(best_scores)]
    best_score = round(best_score + max(team_predictions.loc[best_team, 'expected_points']), 2)
    return {
        'best_team': best_team,
        'best_score': best_score
    }


def get_squad_predictions(team_id, custom_transfers):
    # Fetch the previous gameweek and the team picks
    data_fetcher = DataFetcher(team_predict=True)
    prev_gameweek = data_fetcher.next_gameweek - 1
    team = Team(team_id, prev_gameweek, custom_transfers)
    team_picks = team.picks
    # Open the pickled predictions data
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    filename = 'data/predictions.sav'
    predictions = pickle.load(open(os.path.abspath(os.path.join(base, filename)), 'rb'))

    # Select only the id's that are picked, then sort by position and points
    team_predictions = predictions.loc[team_picks, :].drop('value', axis=1).join(team.transfers_in_cost)
    team_predictions.PP.fillna(team_predictions.initial_price, inplace=True)
    team_predictions['SP'] = [
        '{:.1f}'.format((team_predictions.loc[i, 'PP'] + team_predictions.loc[i, 'price']) / 2)
        if team_predictions.loc[i, 'PP'] < team_predictions.loc[i, 'price']
        else team_predictions.loc[i, 'price'] for i in team_predictions.index]
    team_predictions['position'] = team_predictions['position'].map({
        'GKP': 1,
        'DEF': 2,
        'MID': 3,
        'FWD': 4
    })
    team_predictions = team_predictions.sort_values(
        ['position', 'expected_points'], ascending=[True, False]).astype({'SP': 'float64'})
    team_predictions['position'] = team_predictions['position'].map({
        1: 'GKP',
        2: 'DEF',
        3: 'MID',
        4: 'FWD',
    })
    return {
        'team_name': team.team_name,
        'squad_predictions': team_predictions,
        'bank': team.team_info["last_deadline_bank"] / 10
    }


def get_optimal_team_selection(squad_predictions):
    best_comb = find_best_combination(squad_predictions)
    best_score, best_team = best_comb['best_score'], best_comb['best_team']

    squad_predictions_copy = squad_predictions.copy()

    captain_index = squad_predictions_copy.loc[best_team, 'expected_points'].idxmax()
    squad_predictions_copy.loc[captain_index, 'second_name'] = squad_predictions.loc[
                                                                  captain_index, 'second_name'] + ' (C)'
    squad_predictions_copy.loc[captain_index, 'expected_points'] = '2 x {}'.format(
        squad_predictions.loc[captain_index, 'expected_points'])
    return {
        'best_score': best_score,
        'best_team': squad_predictions_copy.loc[best_team, :],
        'captain_name': squad_predictions.loc[captain_index, ['first_name', 'second_name']],
        'captain_score': max(squad_predictions.loc[best_team, 'expected_points']),
    }
