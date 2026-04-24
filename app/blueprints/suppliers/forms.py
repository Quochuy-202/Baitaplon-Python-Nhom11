from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Email

class SupplierForm(FlaskForm):
    name           = StringField('Tên nhà cung cấp', validators=[DataRequired()])
    contact_person = StringField('Người liên hệ', validators=[Optional()])
    phone          = StringField('Số điện thoại', validators=[Optional()])
    email          = StringField('Email', validators=[Optional(), Email()])
    address        = TextAreaField('Địa chỉ', validators=[Optional()])
    tax_code       = StringField('Mã số thuế', validators=[Optional()])
    payment_terms  = TextAreaField('Điều khoản thanh toán', validators=[Optional()])
    notes          = TextAreaField('Ghi chú', validators=[Optional()])
    submit         = SubmitField('Lưu Nhà Cung Cấp')
