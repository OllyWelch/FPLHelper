from data_modelling.team_predict import find_best_combination, get_optimal_team_selection, get_squad_predictions
from data_modelling.data_fetcher import DataFetcher
from itertools import combinations
import numpy as np
import pandas as pd
import pickle
import os


def transfer_recommender(team_id, n_trans, custom_transfers):
    prediction = get_squad_predictions(team_id, custom_transfers)
    bank = prediction['bank']
    current_squad = prediction['squad_predictions']

    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    filename = 'data/predictions.sav'
    predictions = pickle.load(open(os.path.abspath(os.path.join(base, filename)), 'rb'))

    def check_comb(comb, other_player_predictions, team_counts, player_positions, available_funds):
        comb_predictions = other_player_predictions.loc[comb, ['position', 'price', 'team', 'expected_points']]
        new_team_counts = team_counts.add(
            comb_predictions['team'].value_counts()).fillna(comb_predictions['team'].value_counts()).fillna(
            team_counts).values
        return np.array_equal(comb_predictions['position'].astype('str').values, player_positions) and sum(
            comb_predictions['price'].values) <= available_funds \
            and np.array_equal(np.where(new_team_counts < 4, new_team_counts, -1), new_team_counts)

    def get_comb_score(comb, copy_columns, team_player_ids):
        copy = current_squad.copy()
        copy.loc[team_player_ids, copy_columns] = predictions.loc[comb, copy_columns].values
        return (*team_player_ids, *comb, find_best_combination(copy)['best_score'])

    def find_player_transfers(team_player_ids):
        n_transfers = len(team_player_ids)
        team_player_prices = current_squad.loc[team_player_ids, 'SP']
        available_funds = round(bank + sum(team_player_prices), 1)

        player_positions = predictions.loc[team_player_ids, 'position'].sort_values().astype('str').values
        other_player_indices = np.setdiff1d(predictions.index.values, current_squad.index.values)
        other_player_predictions = predictions.loc[other_player_indices, :]
        other_player_predictions = other_player_predictions[other_player_predictions.expected_points > 3.5]

        team_counts = current_squad['team'].value_counts()
        teams_out = predictions.loc[team_player_ids, 'team'].value_counts()
        team_counts = team_counts.sub(teams_out).fillna(team_counts)

        player_id_combs = np.array(list(combinations(
            other_player_predictions[(other_player_predictions.price <= available_funds - 3.9 * (n_transfers - 1))
                                     & (other_player_predictions.position.isin(player_positions))
                                     ].index, n_transfers)))

        # validate each player id comb
        const = len(player_id_combs)
        is_valid_combs = np.array(
            list(map(check_comb, player_id_combs, [other_player_predictions] * const,
                     [team_counts] * const, [player_positions] * const, [available_funds] * const)))
        valid_combs = (player_id_combs.T * is_valid_combs).T
        valid_combs = valid_combs[valid_combs != 0].reshape(sum(is_valid_combs), n_transfers)
        copy_columns = ['position', 'first_name', 'second_name', 'price', 'initial_price',
                        'team', 'expected_points']
        return np.array(
            list(map(get_comb_score, valid_combs, [copy_columns] * len(valid_combs), [team_player_ids] * len(valid_combs))))

    max_pts = current_squad.sort_values('expected_points', ascending=False).reset_index().iloc[4, -3]
    # Find all the combs of n_trans players to transfer out of the team
    combs = list(combinations(current_squad[current_squad.expected_points < max_pts].sort_values('expected_points', ascending=False).index[:], n_trans))
    # Pool the process of finding the best possible replacement for each comb of n_trans players, sort by score
    # and show the top n
    columnlist = ['out_{}'.format(i) for i in range(1, n_trans + 1)] + ['in_{}'.format(i) for i in
                                                                        range(1, n_trans + 1)] + ['score']
    try:
        best_transfers = pd.DataFrame(
            np.array([lst for comb in combs for lst in find_player_transfers(comb)]),
            columns=columnlist).drop_duplicates(subset=['in_{}'.format(i) for i in range(1, n_trans+1)])
        best_transfers = best_transfers.sort_values('score', ascending=False).reset_index(drop=True)
    except:
        return None
    # Replace each player id by their name using the player_names table, reindexing each time
    data_fetcher = DataFetcher()
    names = data_fetcher.player_names.set_index('id')
    for i in range(1, n_trans + 1):

        best_transfers = best_transfers.set_index(['out_{}'.format(i), 'in_{}'.format(i)])

        new_column_list = []
        for j in range(1, i):
            new_column_list += ['out_{}_first_name'.format(j), 'out_{}_second_name'.format(j)]
        for k in range(1, i):
            new_column_list += ['in_{}_first_name'.format(k), 'in_{}_second_name'.format(k)]
        new_column_list += ['first_name', 'second_name', 'score'] + \
                           ['out_{}'.format(j) for j in range(i + 1, n_trans + 1)] + \
                           ['in_{}'.format(j) for j in range(i + 1, n_trans + 1)]

        best_transfers = best_transfers.join(names, on='out_{}'.format(i)).reindex(
            columns=new_column_list).rename(
            columns={'first_name': 'out_{}_first_name'.format(i), 'second_name': 'out_{}_second_name'.format(i)}
        )

        new_column_list = []
        for j in range(1, i + 1):
            new_column_list += ['out_{}_first_name'.format(j), 'out_{}_second_name'.format(j)]
        for k in range(1, i):
            new_column_list += ['in_{}_first_name'.format(k), 'in_{}_second_name'.format(k)]
        new_column_list += ['first_name', 'second_name', 'score'] + \
                           ['out_{}'.format(j) for j in range(i + 1, n_trans + 1)] + \
                           ['in_{}'.format(j) for j in range(i + 1, n_trans + 1)]
        best_transfers = best_transfers.join(names, on='in_{}'.format(i)).reindex(
            columns=new_column_list).rename(
            columns={'first_name': 'in_{}_first_name'.format(i), 'second_name': 'in_{}_second_name'.format(i)}
        ).reset_index()
    return best_transfers


def choose_transfer(out_ids, in_ids, current_squad, predictions):
    current_squad = current_squad.drop(columns=['PP', 'SP', 'initial_price'])
    predictions = predictions.drop(columns=['value'])
    for i in range(len(out_ids)):
        current_squad.loc[out_ids[i], :] = predictions.loc[in_ids[i], :].values
        current_squad.index = pd.Series(current_squad.index).replace(
            {out_ids[i]: in_ids[i]})
    return get_optimal_team_selection(current_squad)
