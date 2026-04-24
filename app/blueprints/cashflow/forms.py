from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from app.models.cashflow import CashTransaction

class TransactionForm(FlaskForm):
    transaction_type = SelectField('Loại phiếu', choices=[('in', 'Phiếu Thu (Income)'), ('out', 'Phiếu Chi (Expense)')])
    category         = SelectField('Hạng mục', validators=[DataRequired()])
    amount           = DecimalField('Số tiền', validators=[DataRequired(), NumberRange(min=1)])
    description      = TextAreaField('Mô tả chi tiết', validators=[DataRequired()])
    submit           = SubmitField('Lưu Phiếu')
