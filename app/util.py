from flask import url_for
from flask_login import current_user


def posts_to_dict(posts):
    final_dict = {}
    c = 0
    for post in posts:
        post_dict = {'id': post.id,
                     'thread_id': post.thread,
                     'order': c,
                     'body': post.body,
                     'timestamp': post.timestamp,
                     'author': post.author.username,
                     'profile': url_for('profile.profile', username=post.author.username),
                     'avatar': post.author.avatar(50),
                     'likes': post.likes.count(),
                     'language': post.language,
                     'is_current_user': current_user.id == post.user_id if not current_user.is_anonymous else False,
                     'current_user_has_liked': current_user.has_liked_post(
                         post) if not current_user.is_anonymous else False}
        final_dict['post_{}'.format(c)] = post_dict
        c += 1
    return final_dict


def threads_to_dict(threads):
    final_thread_dict = {}
    c = 0
    for thread in threads:
        thread_dict = {'id': thread.id,
                       'name': thread.name}
        final_thread_dict['thread_{}'.format(c)] = thread_dict
        c += 1
    return final_thread_dict


def single_post_to_dict(post):
    return {'id': post.id,
            'thread_id': post.thread,
            'order': 0,
            'body': post.body,
            'timestamp': post.timestamp,
            'author': post.author.username,
            'profile': url_for('profile.profile', username=post.author.username),
            'avatar': post.author.avatar(150),
            'likes': post.likes.count(),
            'language': post.language,
            'is_current_user': current_user.id == post.user_id if not current_user.is_anonymous else False,
            'current_user_has_liked': current_user.has_liked_post(
                post) if not current_user.is_anonymous else False}


def user_to_dict(user):
    return {'id': user.id,
            'username': user.username,
            'about': user.about_me,
            'avatar': user.avatar(70)}