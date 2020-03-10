import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from flask_apscheduler import APScheduler
from redis import Redis
from rq import Queue
import time
from config import Config
from app.tasks import update_predictions

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()
scheduler = APScheduler()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)
    scheduler.init_app(app)

    scheduler.start()

    app.connection = Redis.from_url(app.config['REDIS_URL'])
    app.queue = Queue('fplhelper-tasks', connection=app.connection, default_timeout=3600)

    # Save an initial predictions and next_gameweek file to disk on initial load
    update_predictions()

    def send_task_to_worker():
        """Scheduled function which sends each task sequentially to a single
        Redis worker."""
        # Update data in job1
        print('Data update started...')
        job1 = app.queue.enqueue('app.tasks.update_data', job_timeout=3600)

        # wait until job1 is complete
        while not job1.is_finished:
            time.sleep(1)
        print('Data update completed.')

        # Update model and predictions with job2
        print('Model and predictions updating...')
        job2 = app.queue.enqueue('app.tasks.update_predictions', job_timeout=3600)

        # wait until job2 is complete
        while not job2.is_finished:
            time.sleep(1)
        print('Model and predictions updated.')

    scheduler.add_job(func=send_task_to_worker, trigger='interval', minutes=60,
                      id='worker_task',
                      timezone="Europe/London")

    app.engine = db.create_engine(app.config['FPL_DATABASE_URI'], engine_opts={})

    from app.blueprints.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.blueprints.tools import bp as tools_bp
    app.register_blueprint(tools_bp, url_prefix='/tools')

    from app.blueprints.forum import bp as forum_bp
    app.register_blueprint(forum_bp, url_prefix='/forum')

    from app.blueprints.profile import bp as profile_bp
    app.register_blueprint(profile_bp)

    from app.blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='FPLHelper Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/FPLHelper.log',
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('FPLHelper startup')
    return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


from app import models
