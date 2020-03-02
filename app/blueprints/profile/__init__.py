from flask import Blueprint

bp = Blueprint('profile', __name__)

from app.blueprints.profile import routes
