from data_modelling.team_predict import find_best_combination, get_optimal_team_selection, get_squad_predictions
from data_modelling.data_fetcher import DataFetcher
from itertools import combinations
import numpy as np
import pandas as pd
import pickle
import os


def check_comb(comb, other_player_predictions, team_counts, player_positions, available_funds):
    """Helper function in main transfer recommender function which given a
    dataframe of player predictions not in current squad, team counts without transferred out players,
     positions of transferred out players, and available funds, determines if the given combination of
     player ids is a valid transfer"""

    # get prediction data for the given comb
    comb_predictions = other_player_predictions.loc[comb, ['position', 'first_name', 'second_name', 'price',
                                                           'initial_price', 'team', 'expected_points']]
    # get the counts for each team of the new combination
    comb_team_value_counts = comb_predictions['team'].value_counts()

    # return whether the given combination is of the right positions, costs below available funds, and
    # there is no violation of the "max 3 players from one team rule"
    return [np.array_equal(comb_predictions['position'].astype('str').values, player_positions) and sum(
        comb_predictions['price'].values) <= available_funds \
            and not np.any(team_counts.add(
                comb_team_value_counts).fillna(comb_team_value_counts).fillna(
                team_counts).values > 3), comb_predictions]


def get_comb_score(comb, unchanged, team_player_ids):
    """Returns the new score of a valid combination of transfers calculated with
    the find_best_combination function. Also passes through the values of the player
    ids of the transferred out and transferred in players"""

    return (*team_player_ids, *comb.index.values, find_best_combination(
        pd.concat([unchanged, comb]))['best_score'])


def find_player_transfers(team_player_ids, other_player_predictions, current_squad, bank):
    """Given a list of players to transfer out, a dataframe of other players predictions,
    a dataframe showing the current squad, the current bank value, returns all valid
    transfers for the players transferred out and their respective scores"""

    # get the number of transfers required
    n_trans = len(team_player_ids)

    # calculate newly available funds after transferring players out
    available_funds = round(bank + sum(current_squad.loc[team_player_ids, 'SP']), 1)

    # get the positions of the players transferred out for passing into check_comb function
    player_positions = current_squad.loc[team_player_ids, 'position'].astype('str').values

    # get the team counts for the current squad without the transferred out players
    team_counts = current_squad.loc[np.setdiff1d(current_squad.index, team_player_ids), 'team'].value_counts()

    # get all the valid transfer combinations,
    player_id_combs = np.array(list(combinations(
        other_player_predictions[(other_player_predictions.price <= available_funds - 3.9 * (n_trans - 1))
                                 & (other_player_predictions.position.isin(player_positions))
                                 ].index, n_trans)))

    # validate each player id comb
    const = len(player_id_combs)
    is_valid_combs = np.array(
        list(map(check_comb, player_id_combs, [other_player_predictions] * const,
                 [team_counts] * const, [player_positions] * const, [available_funds] * const)))

    # select only those that are valid
    valid_combs = is_valid_combs[list(is_valid_combs[:, 0])][:, 1]

    # get the unchanged rows from the current_squad
    copy_columns = ['position', 'first_name', 'second_name', 'price', 'initial_price',
                    'team', 'expected_points']
    unchanged = current_squad.loc[np.setdiff1d(current_squad.index.values, team_player_ids), copy_columns]

    # Finally return the scores of each valid combination in an array
    return np.array(
        list(map(get_comb_score, valid_combs, [unchanged] * len(valid_combs),
                 [team_player_ids] * len(valid_combs))))


def transfer_recommender(team_id, n_trans, custom_transfers, manual_engine=None):
    """Function which given a team's ID, number of transfers and any extra transfers
    that have already been made, returns a pandas dataframe of recommended transfers for the
    given team. The transfers recommended are those that maximise best score attribute of the
    find_best_combination function in team_predict.py"""

    # Get the current predictions of the given team id and the value of their bank at present
    prediction = get_squad_predictions(team_id, custom_transfers)
    bank = prediction['bank']
    current_squad = prediction['squad_predictions']

    # Load the dataframe of predictions so we can compare the current squad predictions with
    # predictions of players not in the squad
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    filename = 'data/predictions.sav'
    predictions = pickle.load(open(os.path.abspath(os.path.join(base, filename)), 'rb'))

    # Find all the combs of n_trans players to transfer out of the team
    # cutoff reduces the number of combinations to check
    cutoff = 0 if n_trans == 1 else 7
    combs = list(combinations(current_squad.sort_values('expected_points', ascending=False).index[cutoff:], n_trans))

    # get all the predictions of players not in the current squad, satisfying some minimum points requirement
    other_player_predictions = predictions.loc[
                               np.setdiff1d(predictions.index.values, current_squad.index.values), :]
    other_player_predictions = other_player_predictions[other_player_predictions.expected_points > 3.5]

    # get all transfers for each combination and put them in a big dataframe, sorted by new score high to low
    columnlist = ['out_{}'.format(i) for i in range(1, n_trans + 1)] + ['in_{}'.format(i) for i in
                                                                        range(1, n_trans + 1)] + ['score']
    best_transfers = pd.DataFrame(
        np.array([lst for comb in combs for lst in find_player_transfers(comb, other_player_predictions,
                                                                               current_squad, bank)]),
        columns=columnlist)

    # drop any duplicate transfers in
    best_transfers = best_transfers.sort_values('score', ascending=False).drop_duplicates(
        subset=['in_{}'.format(i) for i in range(1, n_trans + 1)]).reset_index(drop=True)

    # Replace each player id by their name using the player_names table, reindexing each time
    data_fetcher = DataFetcher(manual_engine=manual_engine)
    names = data_fetcher.get_player_names().set_index('id').loc[:, ['first_name', 'second_name']]

    for i in range(1, n_trans + 1):
        # set the index on the ids for the i-th transfer
        best_transfers = best_transfers.set_index(['out_{}'.format(i), 'in_{}'.format(i)])

        # join the players name for the player transferred out
        best_transfers = best_transfers.join(names, on='out_{}'.format(i)).rename(
            columns={'first_name': 'out_{}_first_name'.format(i), 'second_name': 'out_{}_second_name'.format(i)}
        )

        # join the players name for the player transferred in, and reset the index
        best_transfers = best_transfers.join(names, on='in_{}'.format(i)).rename(
            columns={'first_name': 'in_{}_first_name'.format(i), 'second_name': 'in_{}_second_name'.format(i)}
        ).reset_index()

    # create a list of columns for the final reindexing
    columnlist = ['out_{}'.format(i) for i in range(1, n_trans + 1)] + ['in_{}'.format(i) for i in range(1, n_trans + 1)]

    for direction in ['out', 'in']:
        for transfer in range(1, n_trans + 1):
            columnlist += ['{}_{}_first_name'.format(direction, transfer), '{}_{}_second_name'.format(direction, transfer)]

    columnlist.append('score')

    # return the re-indexed dataframe
    return best_transfers.reindex(columns=columnlist)


def choose_transfer(out_ids, in_ids, current_squad, predictions):
    """Allows a user to choose a transfer, which shows them the new predictions for their
    squad given the ids of the players transferred out and in respectively."""

    # drop any unnecessary columns
    current_squad = current_squad.drop(columns=['PP', 'SP', 'initial_price'])
    predictions = predictions.drop(columns=['value'])

    # replace the current squad values by the predicted values of those transferred in
    for i in range(len(out_ids)):
        current_squad.loc[out_ids[i], :] = predictions.loc[in_ids[i], :].values
        current_squad.index = pd.Series(current_squad.index).replace(
            {out_ids[i]: in_ids[i]})

    # return the optimal team selection of the newly changed squad
    return get_optimal_team_selection(current_squad)
