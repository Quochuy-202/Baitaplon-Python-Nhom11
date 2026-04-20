from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional

class ProductForm(FlaskForm):
    # Dùng string cho category_id và unit_id để dễ set choices động từ route
    category_id = SelectField('Danh mục', validators=[DataRequired()])
    unit_id     = SelectField('Đơn vị tính', validators=[DataRequired()])
    
    name            = StringField('Tên sản phẩm', validators=[DataRequired()])
    sku             = StringField('Mã nội bộ (SKU)', validators=[Optional()])
    barcode         = StringField('Mã vạch (Barcode)', validators=[Optional()])
    description     = TextAreaField('Mô tả', validators=[Optional()])
    
    cost_price      = DecimalField('Giá vốn', validators=[DataRequired()], default=0)
    retail_price    = DecimalField('Giá bán lẻ', validators=[DataRequired()], default=0)
    wholesale_price = DecimalField('Giá bán sỉ', validators=[Optional()], default=0)
    
    stock_quantity  = IntegerField('Tồn kho hiện tại', validators=[Optional()], default=0)
    min_stock       = IntegerField('Tồn tối thiểu', validators=[DataRequired()], default=5)
    max_stock       = IntegerField('Tồn tối đa', validators=[Optional()], default=500)
    
    location        = StringField('Vị trí kệ', validators=[Optional()])
    
    submit          = SubmitField('Lưu Sản Phẩm')

class CategoryForm(FlaskForm):
    name        = StringField('Tên danh mục', validators=[DataRequired()])
    parent_id   = SelectField('Danh mục cha', coerce=int, validators=[Optional()])
    description = TextAreaField('Mô tả', validators=[Optional()])
    icon        = StringField('Icon (FontAwesome)', validators=[Optional()], default='fa-box')
    submit      = SubmitField('Lưu Danh Mục')
