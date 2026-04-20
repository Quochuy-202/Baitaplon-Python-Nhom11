from flask import render_template
from flask_login import login_required
from . import inventory_bp

@inventory_bp.route('/')
@login_required
def index():
    return "Inventory Module Pending"
