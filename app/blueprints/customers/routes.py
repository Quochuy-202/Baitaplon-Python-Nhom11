from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from . import customers_bp
from .forms import CustomerForm
from app.extensions import db
from app.models import Customer

@customers_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '')
    
    query = Customer.query
    if q:
        query = query.filter(db.or_(
            Customer.name.ilike(f'%{q}%'),
            Customer.phone.ilike(f'%{q}%'),
            Customer.company_name.ilike(f'%{q}%')
        ))
    
    pagination = query.order_by(Customer.id.desc()).paginate(page=page, per_page=15)
    return render_template('customers/index.html', pagination=pagination, customers=pagination.items, q=q)

@customers_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(
            customer_type=form.customer_type.data,
            name=form.name.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data,
            birth_date=form.birth_date.data,
            company_name=form.company_name.data,
            tax_code=form.tax_code.data,
            representative=form.representative.data,
            notes=form.notes.data,
            card_level=form.card_level.data,
            debt_amount=form.debt_amount.data or 0
        )
        db.session.add(customer)
        db.session.commit()
        flash('Đã thêm khách hàng mới.', 'success')
        return redirect(url_for('customers.index'))
    return render_template('customers/form.html', form=form, title='Thêm Khách Hàng')

@customers_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    customer = Customer.query.get_or_404(id)
    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        form.populate_obj(customer)
        db.session.commit()
        flash('Đã cập nhật thông tin khách hàng.', 'success')
        return redirect(url_for('customers.index'))
    return render_template('customers/form.html', form=form, title='Sửa Khách Hàng')

@customers_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    customer = Customer.query.get_or_404(id)
    # Check if has orders
    if customer.orders.count() > 0:
        flash('Không thể xóa khách hàng đã có lịch sử mua hàng.', 'warning')
    else:
        db.session.delete(customer)
        db.session.commit()
        flash('Đã xóa khách hàng.', 'success')
    return redirect(url_for('customers.index'))

@customers_bp.route('/api/list')
@login_required
def api_list():
    customers = Customer.query.order_by(Customer.name).all()
    return [{
        'id': c.id,
        'name': c.display_name,
        'phone': c.phone
    } for c in customers]
