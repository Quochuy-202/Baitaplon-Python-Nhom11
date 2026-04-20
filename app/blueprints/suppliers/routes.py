from flask import render_template
from flask_login import login_required
from . import suppliers_bp

@suppliers_bp.route('/')
@login_required
def index():
    return "Suppliers Module Pending"
