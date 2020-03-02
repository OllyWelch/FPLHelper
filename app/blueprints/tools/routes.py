from flask import render_template, request, jsonify, flash
from flask_login import current_user, login_required
from app.blueprints.tools import bp
from app.models import UserTransfer
from app import db
import pandas as pd
import numpy as np
from data_modelling.team_predict import get_squad_predictions, get_optimal_team_selection
from data_modelling.predictions_retrieve import get_predictions
from data_modelling.transfer_recommend import transfer_recommender, choose_transfer
from data_modelling.data_fetcher import DataFetcher


@bp.route('/team-selector', methods=['GET', 'POST'])
@login_required
def team_selector():
    return render_template(
        'tools/team_selector.html', title='Team Selector')


@bp.route('/predictions', methods=['POST'])
@login_required
def predictions():
    data = get_predictions()
    gameweek = data['next_gameweek']
    team_id = current_user.team_id
    transfers = UserTransfer.query.filter_by(user_id=current_user.id).all()
    transfer_list = []
    for transfer in transfers:
        transfer_list.append([transfer.out_id, transfer.in_id])
    squad = get_squad_predictions(team_id, transfer_list)
    squad['squad_predictions'] = squad['squad_predictions'].rename(
        columns={'position': 'Position', 'first_name': 'First Name',
                 'second_name': 'Second Name',
                 'expected_points': 'Expected Points'}).to_html(index=False,
                                                                columns=['Position', 'First Name', 'Second Name', 'Expected Points'],
                                                                classes="table table-striped table-hover table-condensed")
    return jsonify({'gameweek': gameweek, 'squadName': squad['team_name'], 'squadPredictions': squad['squad_predictions']})


@bp.route('/get_optimal_team', methods=['POST'])
@login_required
def get_optimal_team():
    squad_predictions = pd.read_html("""{}""".format(request.form['team']))[0].rename(
        columns={'Position': 'position', 'First Name': 'first_name',
                 'Second Name': 'second_name', 'Expected Points': 'expected_points'})
    squad_predictions.index = squad_predictions.index.rename('id')
    optimal_team = get_optimal_team_selection(squad_predictions)
    return jsonify({'best_score': optimal_team['best_score'],
                    'best_team': optimal_team['best_team'].replace({'GKP': 100, 'DEF': 101, 'MID': 102, 'FWD': 103}).sort_values(by=['position'])
                   .replace({100: 'GKP', 101: 'DEF', 102: 'MID', 103: 'FWD'}).rename(
                        columns={'position': 'Position', 'first_name': 'First Name',
                                 'second_name': 'Second Name',
                                 'expected_points': 'Expected Points'}).to_html(
                        index=False,
                        classes='table table-striped table-hover table-condensed',
                        columns=['Position', 'First Name', 'Second Name', 'Expected Points'])})


@bp.route('/transfer-recommend', methods=['GET', 'POST'])
@login_required
def transfer_recommend():
    return render_template('tools/transfer_recommend.html',
                           title='Transfer Recommender')


@bp.route('/get_recommended_transfers', methods=['POST'])
@login_required
def get_recommended_transfers():
    team_id, n_trans = request.form['team_id'], int(request.form['n_trans'])
    transfers = UserTransfer.query.filter_by(user_id=current_user.id).all()
    transfer_list = []
    for transfer in transfers:
        transfer_list.append([transfer.out_id, transfer.in_id])
    recommended = transfer_recommender(team_id, n_trans, transfer_list)
    return jsonify({'recommended':
                        recommended.rename(
                            columns={'out_1_first_name': 'Out', 'out_1_second_name': '', 'in_1_first_name': 'In',
                                     'in_1_second_name': '', 'score': 'New expected score'}
                        ).to_html(index=False, classes='table table-striped table-hover table-condensed')})


@bp.route('/get_new_team', methods=['POST'])
@login_required
def get_new_team():
    choice, out_id, in_id = int(request.form['choice']), [int(float(request.form['out_id']))], [
        int(float(request.form['in_id']))]
    data = get_predictions()
    predictions = data['predictions']
    transfers = UserTransfer.query.filter_by(user_id=current_user.id).all()
    transfer_list = []
    for transfer in transfers:
        transfer_list.append([transfer.out_id, transfer.in_id])
    squad = get_squad_predictions(current_user.team_id, transfer_list)['squad_predictions']
    new_team = choose_transfer(out_id, in_id, squad, predictions)
    return jsonify({'new_team': new_team['best_team'].replace({'GKP': 100, 'DEF': 101, 'MID': 102, 'FWD': 103}).sort_values(by=['position'])
                   .replace({100: 'GKP', 101: 'DEF', 102: 'MID', 103: 'FWD'}).rename(
        columns={'position': 'Position', 'first_name': 'First Name', 'second_name': 'Second Name', 'expected_points': 'Expected Points'}
    ).to_html(index=False, classes='table table-striped table-hover table-condensed', columns=['Position', 'First Name',
                                                                                               'Second Name', 'Expected Points']),
                    'best_score': new_team['best_score']})


@bp.route('/custom-transfers', methods=['GET', 'POST'])
@login_required
def custom_transfers():
    return render_template('tools/custom_transfers.html', title='Custom Transfers')


@bp.route('/get-valid-transfers', methods=['POST'])
@login_required
def get_valid_transfers():
    transfers = UserTransfer.query.filter_by(user_id=current_user.id).all()
    transfer_list = []
    for transfer in transfers:
        transfer_list.append([transfer.out_id, transfer.in_id])
    squad_predictions = get_squad_predictions(current_user.team_id, transfer_list)
    current_bank = squad_predictions['bank']
    team_counts = squad_predictions['squad_predictions']['team'].value_counts()
    player_out = pd.DataFrame(squad_predictions['squad_predictions'].reset_index().iloc[int(request.form['row']), :]).transpose()
    new_team_counts = pd.DataFrame(team_counts.subtract(
        player_out['team'].value_counts()).fillna(player_out['team'].value_counts()).fillna(
        team_counts))
    forbidden_teams = new_team_counts[new_team_counts.team >= 3].index.values
    allowed_teams = pd.Series(np.setdiff1d(np.arange(1, 21), forbidden_teams))
    team_dict = {
        1: 'ARS',
        2: 'AVL',
        3: 'BOU',
        4: 'BHA',
        5: 'BUR',
        6: 'CHE',
        7: 'CRY',
        8: 'EVE',
        9: 'LEI',
        10: 'LIV',
        11: 'MCI',
        12: 'MUN',
        13: 'NEW',
        14: 'NOR',
        15: 'SHU',
        16: 'SOU',
        17: 'TOT',
        18: 'WAT',
        19: 'WHU',
        20: 'WOL'
    }
    allowed_teams = allowed_teams.map(team_dict)
    player_out_sp = player_out['SP'].values[0]
    retrieve_predictions = get_predictions()
    other_player_predictions = retrieve_predictions['predictions']
    valid_players = other_player_predictions[(other_player_predictions.position == player_out.loc[:, 'position'].values[0]) &
                                             (other_player_predictions.price <= player_out_sp + current_bank) &
                                             (np.isin(other_player_predictions.team, allowed_teams)) &
                                             (np.isin(other_player_predictions.index.values,
                                                         np.setdiff1d(other_player_predictions.index.values,
                                                                      squad_predictions['squad_predictions'].reset_index()['id'].values)))]
    return jsonify({'out_id': str(player_out['id'].values[0]), 'validPlayers': valid_players.rename(
        columns={'position': 'Position', 'first_name': 'First Name',
                 'second_name': 'Second Name', 'price': 'Price', 'team': 'Team', 'expected_points': 'Expected Points'}
    ).to_html(classes='table table-striped table-hover table-condensed', columns=['Position', 'Team', 'First Name',
                                                                                               'Second Name', 'Price',
                                                                                               'Expected Points']),
                    })


@bp.route('/add_transfer', methods=['POST'])
@login_required
def add_transfer():
    data = get_predictions()
    gameweek = data['next_gameweek']
    transfer = UserTransfer(user_id=current_user.id, out_id=request.form['out_id'], in_id=request.form['in_id'],
                            gameweek=gameweek)
    db.session.add(transfer)
    db.session.commit()
    flash('Transfer successfully added')
    return jsonify({})


@bp.route('/get_custom_transfers', methods=['POST'])
@login_required
def get_custom_transfers():
    data = get_predictions()
    gameweek = data['next_gameweek']
    transfers = UserTransfer.query.filter_by(user_id=current_user.id, gameweek=gameweek).all()
    transfer_list = []
    for transfer in transfers:
        transfer_list.append([transfer.out_id, transfer.in_id])
    transfers = pd.DataFrame(transfer_list, columns=['Out', 'In']).set_index('Out')
    data_fetcher = DataFetcher()
    player_names = data_fetcher.player_names.loc[:, ['id', 'first_name', 'second_name']].set_index('id')
    transfers = transfers.join(player_names, on='Out').reset_index(drop=True).rename(columns={
        'first_name': 'Out', 'second_name': ''
    }).set_index('In').join(
        player_names, on='In').reset_index(drop=True).rename(
        columns={'first_name': 'In', 'second_name': ''})
    if len(transfers.index) > 0:
        return jsonify({'transfers': transfers.to_html(index=False, classes='table table-responsive table-hover table-striped')})
    return jsonify({'transfers': '<h4>No custom transfers made.</h4><br>'})


@bp.route('/reset_transfers', methods=['POST'])
@login_required
def reset_transfers():
    transfers = UserTransfer.query.filter_by(user_id=current_user.id).all()
    for transfer in transfers:
        db.session.delete(transfer)
    db.session.commit()
    return jsonify({})


@bp.route('/get_current_user_team_id', methods=['POST'])
@login_required
def get_current_user_team_id():
    return jsonify({'team_id': current_user.team_id})
