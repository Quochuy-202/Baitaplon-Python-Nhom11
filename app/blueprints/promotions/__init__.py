from flask import Blueprint

promotions_bp = Blueprint('promotions', __name__)

from . import routes
