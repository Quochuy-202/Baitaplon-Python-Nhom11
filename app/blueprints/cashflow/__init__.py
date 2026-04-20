from flask import Blueprint

cashflow_bp = Blueprint('cashflow', __name__)

from . import routes
