from flask import Blueprint

bp = Blueprint('forum', __name__)

from app.blueprints.forum import routes
