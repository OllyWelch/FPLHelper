from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from flask_login import UserMixin
from datetime import datetime
from hashlib import md5
from time import time
import json
import jwt


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    team_id = db.Column(db.Integer)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    liked = db.relationship(
        'PostLike',
        foreign_keys='PostLike.user_id',
        backref='user', lazy='dynamic')
    threads = db.relationship('Thread', foreign_keys='Thread.user_id', backref='user', lazy='dynamic')
    transfers = db.relationship('UserTransfer', foreign_keys='UserTransfer.user_id', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user',
                                    lazy='dynamic')
    last_read_time = db.Column(db.DateTime)

    def like_post(self, post):
        if not self.has_liked_post(post):
            if self.id != post.user_id:
                thread = Thread.query.filter_by(id=post.thread).first_or_404()
                notification = Notification(name='new_like', user_id=post.user_id, payload_json=json.dumps({
                    'liked_by': self.username, 'avatar': self.avatar(60), 'post_body': post.body, 'thread_name': thread.name}))
                db.session.add(notification)
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(
                user_id=self.id,
                post_id=post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(
            PostLike.user_id == self.id,
            PostLike.post_id == post.id).count() > 0

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def get_new_notifications(self):
        last_read_time = self.last_read_time or datetime(1900, 1, 1)
        return Notification.query.filter_by(user_id=self.id).filter(
            Notification.timestamp > last_read_time).order_by(Notification.timestamp.desc()).all()

    def get_old_notifications(self):
        last_read_time = self.last_read_time or datetime(1900, 1, 1)
        return Notification.query.filter_by(user_id=self.id).filter(
            Notification.timestamp <= last_read_time).order_by(Notification.timestamp.desc()).all()

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likes = db.relationship('PostLike', backref='post', lazy='dynamic')
    thread = db.Column(db.Integer, db.ForeignKey('thread.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class PostLike(db.Model):
    __tablename__ = 'post_likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    body = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    posts = db.relationship('Post', backref='posts', lazy='dynamic')
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Thread {}>'.format(self.name)

    def add_post(self, post):
        author = User.query.filter_by(id=post.user_id).first_or_404()
        all_other_users = set([post.user_id for post in Post.query.filter_by(thread=self.id).filter(Post.user_id != post.user_id)])
        notifications = [Notification(name='new_post', user_id=user_id, payload_json=json.dumps({
            'author_username': author.username, 'avatar': author.avatar(60), 'post_body': post.body, 'thread_name': self.name
        })) for user_id in all_other_users]
        if post.body != '':
            for n in notifications:
                db.session.add(n)
            db.session.add(post)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    payload_json = db.Column(db.Text)

    def __repr__(self):
        return '<Notification {}>'.format(self.name)

    def get_data(self):
        return json.loads(str(self.payload_json))


class UserTransfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    out_id = db.Column(db.Integer)
    in_id = db.Column(db.Integer)
    gameweek = db.Column(db.Integer)

    def __repr__(self):
        return '<Transfer {}>'.format(self.id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
