from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlsplit

from . import auth_bp
from .forms import LoginForm
from app.models.user import User

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')
            return redirect(url_for('auth.login'))
            
        if not user.is_active:
            flash('Tài khoản đã bị khóa.', 'danger')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=form.remember_me.data)
        
        # Helper để ghi log login -> cần AuditLog model
        from app.models.audit_log import log_action
        from app.extensions import db
        log_action(user.id, 'login', 'user', user.id, 'User logged in', request.remote_addr)
        db.session.commit()
        
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('dashboard.index')
        return redirect(next_page)
        
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        from app.models.audit_log import log_action
        from app.extensions import db
        # Ghi log trước khi logout vì logout sẽ xóa session current_user
        log_action(current_user.id, 'logout', 'user', current_user.id, 'User logged out', request.remote_addr)
        db.session.commit()
        
    logout_user()
    flash('Bạn đã đăng xuất.', 'info')
    return redirect(url_for('auth.login'))
