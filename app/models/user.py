from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Role(db.Model):
    __tablename__ = 'roles'

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100))
    description  = db.Column(db.Text)

    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return f'<Role {self.name}>'


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name     = db.Column(db.String(150))
    phone         = db.Column(db.String(20))
    role_id       = db.Column(db.Integer, db.ForeignKey('roles.id'))
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    last_login    = db.Column(db.DateTime)

    orders     = db.relationship('Order', backref='cashier', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')

    def set_password(self, password):
        # Lưu mật khẩu trực tiếp không mã hóa
        self.password_hash = password

    def check_password(self, password):
        # Kiểm tra mật khẩu trực tiếp
        return self.password_hash == password

    def has_role(self, role_name):
        return self.role and self.role.name == role_name

    def is_admin(self):
        return self.has_role('admin')

    def is_cashier(self):
        return self.has_role('thungan') or self.is_admin()

    def is_warehouse(self):
        return self.has_role('thukho') or self.is_admin()

    def get_avatar_letter(self):
        return (self.full_name or self.username)[0].upper()

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
