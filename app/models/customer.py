from app.extensions import db
from datetime import datetime


class Customer(db.Model):
    __tablename__ = 'customers'

    id               = db.Column(db.Integer, primary_key=True)
    customer_type    = db.Column(db.String(20), default='individual')  # individual / business
    name             = db.Column(db.String(200), nullable=False)
    phone            = db.Column(db.String(20))
    email            = db.Column(db.String(120))
    address          = db.Column(db.Text)
    birth_date       = db.Column(db.Date)
    # Business fields
    company_name     = db.Column(db.String(200))
    tax_code         = db.Column(db.String(50))
    representative   = db.Column(db.String(150))
    # Loyalty
    card_level       = db.Column(db.String(20), default='none')  # none / bronze / silver / gold
    points           = db.Column(db.Integer, default=0)
    debt_amount      = db.Column(db.Numeric(15, 0), default=0)
    notes            = db.Column(db.Text)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    orders = db.relationship('Order', backref='customer', lazy='dynamic')

    @property
    def display_name(self):
        if self.customer_type == 'business' and self.company_name:
            return self.company_name
        return self.name

    @property
    def total_spent(self):
        from app.models.order import Order
        result = db.session.query(db.func.sum(Order.total_amount)).filter(
            Order.customer_id == self.id,
            Order.status == 'completed'
        ).scalar()
        return result or 0

    @property
    def order_count(self):
        return self.orders.filter_by(status='completed').count()

    def card_level_badge(self):
        badges = {'gold': 'warning', 'silver': 'secondary', 'bronze': 'danger', 'none': 'light'}
        return badges.get(self.card_level, 'light')

    def __repr__(self):
        return f'<Customer {self.name}>'
