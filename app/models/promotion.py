from app.extensions import db
from datetime import datetime


class Promotion(db.Model):
    __tablename__ = 'promotions'

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(200), nullable=False)
    description     = db.Column(db.Text)
    promotion_type  = db.Column(db.String(20))   # percentage / fixed / combo
    value           = db.Column(db.Numeric(10, 2), default=0)  # % hoặc số tiền
    min_quantity    = db.Column(db.Integer, default=1)
    min_order_value = db.Column(db.Numeric(15, 0), default=0)
    start_date      = db.Column(db.Date)
    end_date        = db.Column(db.Date)
    is_active       = db.Column(db.Boolean, default=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def is_currently_active(self):
        today = datetime.utcnow().date()
        if not self.is_active:
            return False
        if self.start_date and today < self.start_date:
            return False
        if self.end_date and today > self.end_date:
            return False
        return True

    def type_label(self):
        labels = {'percentage': 'Giảm %', 'fixed': 'Giảm tiền', 'combo': 'Combo'}
        return labels.get(self.promotion_type, self.promotion_type)

    def __repr__(self):
        return f'<Promotion {self.name}>'


class PriceList(db.Model):
    __tablename__ = 'price_lists'

    id                  = db.Column(db.Integer, primary_key=True)
    name                = db.Column(db.String(200), nullable=False)
    description         = db.Column(db.Text)
    customer_type       = db.Column(db.String(30))    # wholesale / agent / teacher
    discount_percentage = db.Column(db.Numeric(5, 2), default=0)
    is_active           = db.Column(db.Boolean, default=True)
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('PriceListItem', backref='price_list', lazy='dynamic',
                            cascade='all, delete-orphan')

    def __repr__(self):
        return f'<PriceList {self.name}>'


class PriceListItem(db.Model):
    __tablename__ = 'price_list_items'

    id            = db.Column(db.Integer, primary_key=True)
    price_list_id = db.Column(db.Integer, db.ForeignKey('price_lists.id'), nullable=False)
    product_id    = db.Column(db.Integer, db.ForeignKey('products.id'))
    price         = db.Column(db.Numeric(15, 0), default=0)

    product = db.relationship('Product', foreign_keys=[product_id])

    def __repr__(self):
        return f'<PriceListItem {self.id}>'
