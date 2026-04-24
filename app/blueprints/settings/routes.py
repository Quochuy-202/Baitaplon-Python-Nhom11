from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import settings_bp
from app.models import User, Role
from app.extensions import db

@settings_bp.route('/')
@login_required
def index():
    users = User.query.all()
    return render_template('settings/index.html', users=users)

@settings_bp.route('/user/new', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.role.name != 'admin':
        flash('Bạn không có quyền thực hiện thao tác này.', 'danger')
        return redirect(url_for('settings.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        full_name = request.form.get('full_name')
        password = request.form.get('password') # Plain text as per user request
        role_id = request.form.get('role_id')
        
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại.', 'danger')
        else:
            new_user = User(username=username, full_name=full_name, role_id=role_id)
            new_user.password = password 
            db.session.add(new_user)
            db.session.commit()
            flash('Đã thêm nhân viên mới.', 'success')
            return redirect(url_for('settings.index'))
            
    roles = Role.query.all()
    return render_template('settings/user_form.html', roles=roles)
