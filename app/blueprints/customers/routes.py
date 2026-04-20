from flask import render_template
from flask_login import login_required
from . import customers_bp

@customers_bp.route('/')
@login_required
def index():
    return "Customers Module Pending"
