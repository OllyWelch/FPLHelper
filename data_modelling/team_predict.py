from data_modelling.team import Team
import numpy as np
import pickle
import os


def get_best_position_comb(positions_dict, formation, position):
    """Given a set of predictions, a formation and a position. Returns the top
    n players from that position in the set of predictions, where n is the number
    of players in that position in the given formation."""
    return positions_dict[position][:formation[position]]


def get_best_formation_comb(positions_dict, formation):
    """Given a set of predictions and a formation, returns the optimal team selection
    for this formation. Uses the get_best_position_comb function for each position."""
    return np.concatenate(np.array(
        list(map(get_best_position_comb, [positions_dict]*len(formation), [formation]*len(formation), formation))))


def find_best_combination(team_predictions):
    """Given a set of predictions, loops through each possible formation, and uses the
    get_best_formation_comb function to find the best selection. Returns the combination
    with the highest total expected score."""
    valid_formations = np.array([{
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
    team_predictions = team_predictions.sort_values('expected_points', ascending=False)
    predictions_dict = {'GKP': team_predictions[team_predictions.position == 'GKP'].reset_index().loc[
                               :, ['id', 'expected_points']].values,
                        'DEF': team_predictions[team_predictions.position == 'DEF'].reset_index().loc[
                               :, ['id', 'expected_points']].values,
                        'MID': team_predictions[team_predictions.position == 'MID'].reset_index().loc[
                               :, ['id', 'expected_points']].values,
                        'FWD': team_predictions[team_predictions.position == 'FWD'].reset_index().loc[
                               :, ['id', 'expected_points']].values}
    best_formation_combs = np.array(list(map(get_best_formation_comb, [predictions_dict]*len(valid_formations),
                                             valid_formations)))
    best_scores = np.array(list(map(
        lambda selection: round(sum(selection[:, 1]) + max(selection[:, 1]), 2),
        best_formation_combs)))
    best_score, best_team = np.amax(best_scores), best_formation_combs[np.argmax(best_scores)][:, 0]
    return {
        'best_team': best_team,
        'best_score': best_score
    }


def get_squad_predictions(team_id, custom_transfers):
    """Returns the set of predictions for each player in the previous gameweek's picks
    for a given team id. Adds any custom transfers which the user may have added"""

    # Fetch the previous gameweek from disk
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    next_gameweek_filename = 'data/next_gameweek.sav'
    next_gameweek = pickle.load(open(os.path.abspath(os.path.join(base, next_gameweek_filename)), 'rb'))
    prev_gameweek = next_gameweek - 1

    # Get team picks for given team id, custom transfers, as well as the retrieved previous gameweek
    team = Team(team_id, prev_gameweek, custom_transfers)
    team_picks = team.get_picks()

    # Open the pickled predictions data
    predictions_filename = 'data/predictions.sav'
    predictions = pickle.load(open(os.path.abspath(os.path.join(base, predictions_filename)), 'rb'))

    # Select only the id's that are picked, then sort by position and points
    team_predictions = predictions.loc[team_picks, :].drop('value', axis=1).join(team.get_transfers_in_cost())
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
    team_info = team.get_info()
    return {
        'team_name': team_info['name'],
        'squad_predictions': team_predictions,
        'bank': team_info["last_deadline_bank"] / 10
    }


def get_optimal_team_selection(squad_predictions):
    """Returns a formatted version of find_best_combination, including captain name and score"""
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
