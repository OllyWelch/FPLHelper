import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    THREADS_PER_PAGE_FORUM = 5
    POSTS_PER_PAGE_PROFILE = 3
    POSTS_PER_PAGE_THREAD = 10
    PER_PAGE_PARAMETER = 20
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['fplhelperreset@gmail.com']
    LANGUAGES = ['en', 'es', 'fr']
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
    FPL_DATABASE_URI = os.environ.get('FPL_DATABASE_URL')
