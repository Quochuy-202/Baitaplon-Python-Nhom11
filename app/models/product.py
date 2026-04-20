from app.extensions import db
from datetime import datetime
import random
import string


class Category(db.Model):
    __tablename__ = 'categories'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(150), nullable=False)
    parent_id   = db.Column(db.Integer, db.ForeignKey('categories.id'))
    description = db.Column(db.Text)
    icon        = db.Column(db.String(50))  # Font Awesome class

    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    products = db.relationship('Product', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'


class Unit(db.Model):
    __tablename__ = 'units'

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(80), nullable=False)       # tập, ram, thùng, chiếc
    abbreviation = db.Column(db.String(20))                        # tập, rm, thùng, c
    description  = db.Column(db.String(200))

    products = db.relationship('Product', backref='unit', lazy='dynamic')

    def __repr__(self):
        return f'<Unit {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(250), nullable=False)
    sku             = db.Column(db.String(50), unique=True)
    description     = db.Column(db.Text)
    category_id     = db.Column(db.Integer, db.ForeignKey('categories.id'))
    unit_id         = db.Column(db.Integer, db.ForeignKey('units.id'))
    cost_price      = db.Column(db.Numeric(15, 0), default=0)    # Giá vốn
    retail_price    = db.Column(db.Numeric(15, 0), default=0)    # Giá lẻ
    wholesale_price = db.Column(db.Numeric(15, 0), default=0)    # Giá sỉ
    stock_quantity  = db.Column(db.Integer, default=0)
    min_stock       = db.Column(db.Integer, default=5)
    max_stock       = db.Column(db.Integer, default=500)
    location        = db.Column(db.String(100))                   # Vị trí kệ
    image_url       = db.Column(db.String(300))
    is_active       = db.Column(db.Boolean, default=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    barcodes         = db.relationship('Barcode', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    order_items      = db.relationship('OrderItem', backref='product', lazy='dynamic')
    stock_movements  = db.relationship('StockMovement', backref='product', lazy='dynamic')

    @property
    def primary_barcode(self):
        bc = self.barcodes.filter_by(is_primary=True).first()
        return bc.barcode if bc else None

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.min_stock

    def profit_margin(self):
        if self.cost_price and self.cost_price > 0:
            return int(((self.retail_price - self.cost_price) / self.cost_price) * 100)
        return 0

    def __repr__(self):
        return f'<Product {self.name}>'


class Barcode(db.Model):
    __tablename__ = 'barcodes'

    id         = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    barcode    = db.Column(db.String(100), unique=True, nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Barcode {self.barcode}>'


def generate_sku():
    """Tự sinh SKU nếu sản phẩm không có mã"""
    return 'VPP-' + ''.join(random.choices(string.digits, k=8))


class StockMovement(db.Model):
    __tablename__ = 'stock_movements'

    id              = db.Column(db.Integer, primary_key=True)
    product_id      = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'))
    movement_type   = db.Column(db.String(20))  # in / out / adjust
    quantity        = db.Column(db.Integer, nullable=False)
    before_qty      = db.Column(db.Integer)
    after_qty       = db.Column(db.Integer)
    reference_type  = db.Column(db.String(50))  # purchase_order / order / manual
    reference_id    = db.Column(db.Integer)
    notes           = db.Column(db.Text)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id])

    def __repr__(self):
        return f'<StockMovement {self.movement_type} {self.quantity}>'
