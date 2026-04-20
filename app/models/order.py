from app.extensions import db
from datetime import datetime


class Order(db.Model):
    __tablename__ = 'orders'

    id              = db.Column(db.Integer, primary_key=True)
    order_code      = db.Column(db.String(30), unique=True)
    customer_id     = db.Column(db.Integer, db.ForeignKey('customers.id'))
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'))
    order_date      = db.Column(db.DateTime, default=datetime.utcnow)
    subtotal        = db.Column(db.Numeric(15, 0), default=0)
    discount_amount = db.Column(db.Numeric(15, 0), default=0)
    total_amount    = db.Column(db.Numeric(15, 0), default=0)
    payment_method  = db.Column(db.String(20), default='cash')  # cash / card / qr
    paid_amount     = db.Column(db.Numeric(15, 0), default=0)
    change_amount   = db.Column(db.Numeric(15, 0), default=0)
    status          = db.Column(db.String(20), default='completed')  # completed / held / cancelled
    notes           = db.Column(db.Text)

    items = db.relationship('OrderItem', backref='order', lazy='dynamic',
                            cascade='all, delete-orphan')

    def calculate_totals(self):
        subtotal = sum(item.total_price for item in self.items)
        self.subtotal = subtotal
        self.total_amount = subtotal - (self.discount_amount or 0)

    def payment_method_label(self):
        labels = {'cash': 'Tiền mặt', 'card': 'Thẻ / POS', 'qr': 'QR Code'}
        return labels.get(self.payment_method, self.payment_method)

    def __repr__(self):
        return f'<Order {self.order_code}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id              = db.Column(db.Integer, primary_key=True)
    order_id        = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id      = db.Column(db.Integer, db.ForeignKey('products.id'))
    product_name    = db.Column(db.String(250))     # lưu tên tại thời điểm bán
    quantity        = db.Column(db.Integer, nullable=False, default=1)
    unit_price      = db.Column(db.Numeric(15, 0), default=0)
    discount_amount = db.Column(db.Numeric(15, 0), default=0)
    total_price     = db.Column(db.Numeric(15, 0), default=0)

    def __repr__(self):
        return f'<OrderItem {self.id}>'
