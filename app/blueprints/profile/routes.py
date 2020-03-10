from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from flask_babel import _
from app import db
from app.models import UserTransfer
from app.blueprints.profile import bp
from app.blueprints.profile.forms import EditProfileForm
from app.models import User, Post, Thread
from app.util import posts_to_dict, threads_to_dict
from datetime import datetime
import pandas as pd
from data_modelling.team import Team


@bp.route('/profile/<username>')
@login_required
def profile(username):
    user_object = User.query.filter_by(username=username).first_or_404()
    transfers = UserTransfer.query.filter_by(user_id=current_user.id).all()
    transfer_list = []
    for transfer in transfers:
        transfer_list.append([transfer.out_id, transfer.in_id])
    team = Team(user_object.team_id, 1, transfer_list)
    n_posts = len(Post.query.filter_by(user_id=user_object.id).all())
    return render_template(
        'profile/profile.html', title='Profile - {}'.format(username),
        user=user_object, transfer_list=pd.DataFrame(transfer_list, columns=['Out', 'In']),
        team_name=team.get_name(), n_posts=n_posts)


@bp.route('/profile/<username>/popup')
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    team_name = Team(user.team_id, 1, {}).get_name()
    return render_template('profile/user_popup.html', user=user, team_name=team_name)


@bp.route('/get_user_posts', methods=['POST'])
def get_user_posts():
    username = request.form['username']
    user_id = User.query.filter_by(username=username).first_or_404().id
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.timestamp.desc()).all()
    threads = Thread.query.all()
    return jsonify({'posts': posts_to_dict(posts), 'threads': threads_to_dict(threads)})


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('profile.profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('profile/edit_profile.html', title='Edit Profile',
                           form=form)


@bp.route('/notifications')
@login_required
def notifications():
    return render_template('/profile/notifications.html', title='Notifications')


@bp.route('/get_notifications', methods=['POST'])
@login_required
def get_notifications():
    new_notifications = current_user.get_new_notifications()
    old_notifications = current_user.get_old_notifications()
    current_user.last_read_time = datetime.utcnow()
    db.session.commit()
    return jsonify({'new_notifications': [{'name': n.name, 'time': n.timestamp, 'data': n.get_data()}
                                          for n in new_notifications],
                    'old_notifications': [{'name': n.name, 'time': n.timestamp, 'data': n.get_data()}
                                          for n in old_notifications]})


@bp.route('/clear_notifications', methods=['POST'])
@login_required
def clear_notifications():
    try:
        old_notifications = current_user.get_old_notifications()
        for n in old_notifications:
            db.session.delete(n)
        db.session.commit()
        return jsonify({'status': 1})
    except:
        return jsonify({'status': 0})
