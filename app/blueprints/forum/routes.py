from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _
from app import db
from app.blueprints.forum import bp
from app.blueprints.forum.forms import ThreadForm
from app.models import User, Post, Thread, PostLike
from app.util import posts_to_dict, threads_to_dict, single_post_to_dict, user_to_dict
from guess_language import guess_language


@bp.route('/index', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    threads = Thread.query.order_by(Thread.timestamp.desc()).paginate(
        page, current_app.config['THREADS_PER_PAGE_FORUM'], False)
    next_url = url_for('forum.index', page=threads.next_num) \
        if threads.has_next else None
    prev_url = url_for('forum.index', page=threads.prev_num) \
        if threads.has_prev else None
    form = ThreadForm()
    if form.validate_on_submit():
        language = guess_language(form.thread_body.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        thread = Thread(name=form.thread_name.data, body=form.thread_body.data, user_id=current_user.id,
                        language=language)
        db.session.add(thread)
        db.session.commit()
        flash(_('Thread successfully added to forum!'))
        return redirect(url_for('forum.index'))
    return render_template('forum/index.html', threads=threads.items, next_url=next_url, prev_url=prev_url, form=form,
                           title='Forum')


@bp.route('/get_thread_posts', methods=['POST'])
def get_thread_posts():
    thread_id = request.form['thread_id']
    posts = Post.query.filter_by(thread=thread_id).order_by(Post.timestamp.desc()).all()
    return jsonify({'posts': posts_to_dict(posts)})


@bp.route('/get_all_posts', methods=['POST'])
def get_all_posts():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    threads = Thread.query.all()
    return jsonify({'posts': posts_to_dict(posts), 'threads': threads_to_dict(threads)})


@bp.route('/make_post', methods=['POST'])
@login_required
def make_post():
    user_id, body, thread_id = current_user.id, request.form['body'], request.form['threadId']
    language = guess_language(body)
    if language == 'UNKNOWN' or len(language) > 5:
        language = ''
    if body == '':
        return jsonify({'status': 0})
    post = Post(user_id=user_id, body=body, thread=thread_id, language=language)
    thread = Thread.query.filter_by(id=thread_id).first_or_404()
    thread.add_post(post)
    db.session.commit()
    return jsonify({'status': 1, 'post': single_post_to_dict(post)})


@bp.route('/like', methods=['POST'])
def like():
    post_id, action = request.form['postId'], request.form['action']
    post = Post.query.filter_by(id=post_id).first_or_404()
    if current_user.is_anonymous:
        return jsonify({'new_count': -1})
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    return jsonify({'new_count': post.likes.count()})


@bp.route('/get_post_likes', methods=['POST'])
def get_post_likes():
    post_id = request.form['post_id']
    likes = PostLike.query.filter_by(post_id=post_id).all()
    users = [User.query.filter_by(id=post_like.user_id).first_or_404() for post_like in likes]
    return jsonify({'likes': [user_to_dict(user) for user in users]})


@bp.route('/delete/thread', methods=['POST'])
@login_required
def delete_thread():
    thread_id = request.form['thread_id']
    thread = Thread.query.filter_by(id=thread_id).first_or_404()
    posts = Post.query.filter_by(thread=thread.id).all()
    if current_user.id == thread.user_id:
        db.session.delete(thread)
        for post in posts:
            db.session.delete(post)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'fail'})


@bp.route('/delete_post', methods=['POST'])
@login_required
def delete_post():
    post_id = request.form['id']
    post = Post.query.filter_by(id=post_id).first_or_404()
    db.session.delete(post)
    db.session.commit()
    return jsonify({'Status': 'Success'})
