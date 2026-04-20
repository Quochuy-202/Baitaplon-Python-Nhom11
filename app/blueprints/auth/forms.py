from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    remember_me = BooleanField('Nhớ mật khẩu')
    submit = SubmitField('Đăng nhập')
