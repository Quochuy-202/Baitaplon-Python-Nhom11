from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import cashflow_bp
from .forms import TransactionForm
from app.extensions import db
from app.models.cashflow import CashTransaction

@cashflow_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    t_type = request.args.get('type', '')
    
    query = CashTransaction.query
    if t_type:
        query = query.filter_by(transaction_type=t_type)
        
    pagination = query.order_by(CashTransaction.created_at.desc()).paginate(page=page, per_page=15)
    
    # Calculate balance
    total_in = db.session.query(db.func.sum(CashTransaction.amount)).filter_by(transaction_type='in').scalar() or 0
    total_out = db.session.query(db.func.sum(CashTransaction.amount)).filter_by(transaction_type='out').scalar() or 0
    balance = total_in - total_out
    
    return render_template('cashflow/index.html', 
                           pagination=pagination, 
                           transactions=pagination.items,
                           total_in=total_in,
                           total_out=total_out,
                           balance=balance,
                           t_type=t_type)

@cashflow_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    form = TransactionForm()
    # Populate categories based on type
    form.category.choices = [(k, v) for k, v in CashTransaction.CATEGORY_LABELS.items()]
    
    if form.validate_on_submit():
        transaction = CashTransaction(
            user_id=current_user.id,
            transaction_type=form.transaction_type.data,
            category=form.category.data,
            amount=form.amount.data,
            description=form.description.data,
            reference_type='manual'
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Đã tạo phiếu mới thành công.', 'success')
        return redirect(url_for('cashflow.index'))
        
    return render_template('cashflow/form.html', form=form, title='Tạo Phiếu Thu/Chi')
