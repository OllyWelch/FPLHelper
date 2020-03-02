from flask import render_template, request, jsonify, g, current_app
from flask_login import current_user
from flask_babel import get_locale
from datetime import datetime
from app.blueprints.main import bp
from app import db
import time
from data_modelling.predictions_retrieve import get_predictions


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('main/index.html', title='Home')


@bp.route('/index-predictions', methods=['POST'])
def index_predictions():
    data = get_predictions()
    gameweek = data['next_gameweek']
    predictions = data['predictions']
    return jsonify({'gameweek': gameweek, 'predictions': predictions.rename(
        columns={'position': 'Position', 'first_name': 'First Name',
                 'second_name': 'Second Name',
                 'expected_points': 'Expected Points', 'team': 'Team',
                 'value': 'Value', 'price': 'Price'}).to_html(
        index=False, classes="table table-responsive table-hover table-striped", table_id="index_table",
        columns=['Position', 'Team', 'First Name', 'Second Name', 'Price', 'Expected Points', 'Value'])})


@bp.route('/get_sorted_table', methods=['POST'])
def get_sorted_table():
    data = get_predictions()
    predictions = data['predictions']
    columns = ['position', 'team', 'first_name', 'second_name', 'price', 'expected_points', 'value']
    columns_ascending = {'position': True,
                         'team': True,
                         'first_name': True,
                         'second_name': True,
                         'price': False,
                         'expected_points': False,
                         'value': False}
    column = columns[int(request.form['column']) - 1]
    ascending = columns_ascending[column]
    return jsonify({'predictions': predictions.sort_values(column, ascending=ascending).rename(
        columns={'position': 'Position', 'first_name': 'First Name',
                 'second_name': 'Second Name',
                 'expected_points': 'Expected Points', 'team': 'Team',
                 'value': 'Value', 'price': 'Price'}).to_html(
        index=False, classes="table table-responsive table-hover table-striped", table_id="index_table",
        columns=['Position', 'Team', 'First Name', 'Second Name', 'Price', 'Expected Points', 'Value'])})


@bp.route('/about')
def about():
    return render_template('main/about.html', title='About')
