from app.extensions import db
from datetime import datetime


class CashTransaction(db.Model):
    __tablename__ = 'cash_transactions'

    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'))
    transaction_type = db.Column(db.String(10), nullable=False)   # in / out
    category         = db.Column(db.String(50))
    # in:  sales, debt_collection, other_income
    # out: salary, rent, utilities, supplier_payment, other_expense
    amount           = db.Column(db.Numeric(15, 0), nullable=False)
    description      = db.Column(db.Text)
    reference_type   = db.Column(db.String(50))   # order / purchase_order / manual
    reference_id     = db.Column(db.Integer)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id])

    CATEGORY_LABELS = {
        'sales':            'Thu bán hàng',
        'debt_collection':  'Thu nợ KH',
        'other_income':     'Thu khác',
        'salary':           'Chi lương',
        'rent':             'Chi thuê mặt bằng',
        'utilities':        'Chi điện/nước/internet',
        'supplier_payment': 'Chi trả NCC',
        'other_expense':    'Chi khác',
    }

    def category_label(self):
        return self.CATEGORY_LABELS.get(self.category, self.category)

    def __repr__(self):
        return f'<CashTransaction {self.transaction_type} {self.amount}>'
