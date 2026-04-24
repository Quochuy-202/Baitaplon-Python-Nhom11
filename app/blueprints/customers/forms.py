from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DateField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Optional, Email

class CustomerForm(FlaskForm):
    customer_type  = SelectField('Loại khách hàng', choices=[('individual', 'Cá nhân'), ('business', 'Doanh nghiệp')], default='individual')
    name           = StringField('Tên khách hàng', validators=[DataRequired()])
    phone          = StringField('Số điện thoại', validators=[Optional()])
    email          = StringField('Email', validators=[Optional(), Email()])
    address        = StringField('Địa chỉ', validators=[Optional()])
    birth_date     = DateField('Ngày sinh', validators=[Optional()], format='%Y-%m-%d')
    
    # Doanh nghiệp
    company_name   = StringField('Tên công ty', validators=[Optional()])
    tax_code       = StringField('Mã số thuế', validators=[Optional()])
    representative = StringField('Người đại diện', validators=[Optional()])
    
    notes          = TextAreaField('Ghi chú', validators=[Optional()])
    card_level     = SelectField('Hạng thẻ', choices=[('none', 'Mặc định'), ('bronze', 'Đồng'), ('silver', 'Bạc'), ('gold', 'Vàng')], default='none')
    debt_amount    = DecimalField('Công nợ đầu kỳ', default=0, validators=[Optional()])
    submit         = SubmitField('Lưu Khách Hàng')
