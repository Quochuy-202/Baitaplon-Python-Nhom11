from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class StockAdjustmentForm(FlaskForm):
    product_id    = SelectField('Sản phẩm', validators=[DataRequired()])
    movement_type = SelectField('Loại điều chỉnh', choices=[('in', 'Nhập thêm (Stock In)'), ('out', 'Xuất kho / Hủy (Stock Out)')])
    quantity      = IntegerField('Số lượng', validators=[DataRequired(), NumberRange(min=1)])
    notes         = TextAreaField('Lý do / Ghi chú', validators=[DataRequired()])
    submit        = SubmitField('Xác Nhận Điều Chỉnh')
