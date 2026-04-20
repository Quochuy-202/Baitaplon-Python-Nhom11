from app.extensions import db
from datetime import datetime


class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id               = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(200), nullable=False)
    contact_person   = db.Column(db.String(150))
    phone            = db.Column(db.String(20))
    email            = db.Column(db.String(120))
    address          = db.Column(db.Text)
    tax_code         = db.Column(db.String(50))
    payment_terms    = db.Column(db.Text)    # Điều khoản thanh toán
    debt_amount      = db.Column(db.Numeric(15, 0), default=0)
    notes            = db.Column(db.Text)
    is_active        = db.Column(db.Boolean, default=True)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    purchase_orders = db.relationship('PurchaseOrder', backref='supplier', lazy='dynamic')

    def __repr__(self):
        return f'<Supplier {self.name}>'


class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'

    id              = db.Column(db.Integer, primary_key=True)
    order_code      = db.Column(db.String(30), unique=True)
    supplier_id     = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'))
    order_date      = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount    = db.Column(db.Numeric(15, 0), default=0)
    paid_amount     = db.Column(db.Numeric(15, 0), default=0)
    status          = db.Column(db.String(20), default='pending')  # pending / received / cancelled
    notes           = db.Column(db.Text)

    items = db.relationship('PurchaseOrderItem', backref='purchase_order',
                            lazy='dynamic', cascade='all, delete-orphan')
    user  = db.relationship('User', foreign_keys=[user_id])

    @property
    def remaining_amount(self):
        return (self.total_amount or 0) - (self.paid_amount or 0)

    def __repr__(self):
        return f'<PurchaseOrder {self.order_code}>'


class PurchaseOrderItem(db.Model):
    __tablename__ = 'purchase_order_items'

    id                = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    product_id        = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity          = db.Column(db.Integer, nullable=False, default=1)
    unit_price        = db.Column(db.Numeric(15, 0), default=0)
    total_price       = db.Column(db.Numeric(15, 0), default=0)

    product = db.relationship('Product', foreign_keys=[product_id])

    def __repr__(self):
        return f'<PurchaseOrderItem {self.id}>'
