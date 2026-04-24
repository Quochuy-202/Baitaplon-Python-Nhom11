from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from . import suppliers_bp
from .forms import SupplierForm
from app.extensions import db
from app.models import Supplier

@suppliers_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '')
    
    query = Supplier.query.filter_by(is_active=True)
    if q:
        query = query.filter(db.or_(
            Supplier.name.ilike(f'%{q}%'),
            Supplier.phone.ilike(f'%{q}%'),
            Supplier.contact_person.ilike(f'%{q}%')
        ))
    
    pagination = query.order_by(Supplier.id.desc()).paginate(page=page, per_page=15)
    return render_template('suppliers/index.html', pagination=pagination, suppliers=pagination.items, q=q)

@suppliers_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier(
            name=form.name.data,
            contact_person=form.contact_person.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data,
            tax_code=form.tax_code.data,
            payment_terms=form.payment_terms.data,
            notes=form.notes.data
        )
        db.session.add(supplier)
        db.session.commit()
        flash('Đã thêm nhà cung cấp mới.', 'success')
        return redirect(url_for('suppliers.index'))
    return render_template('suppliers/form.html', form=form, title='Thêm Nhà Cung Cấp')

@suppliers_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    supplier = Supplier.query.get_or_404(id)
    form = SupplierForm(obj=supplier)
    if form.validate_on_submit():
        form.populate_obj(supplier)
        db.session.commit()
        flash('Đã cập nhật thông tin nhà cung cấp.', 'success')
        return redirect(url_for('suppliers.index'))
    return render_template('suppliers/form.html', form=form, title='Sửa Nhà Cung Cấp')

@suppliers_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    supplier = Supplier.query.get_or_404(id)
    
    # Kiểm tra xem có đơn nhập hàng nào không
    if supplier.purchase_orders.count() > 0:
        # Nếu có đơn hàng thì chỉ soft delete
        supplier.is_active = False
        flash(f'Nhà cung cấp {supplier.name} đã có giao dịch nên chỉ được ẩn đi.', 'info')
    else:
        # Nếu chưa có gì thì xóa hẳn
        db.session.delete(supplier)
        flash(f'Đã xóa hoàn toàn nhà cung cấp {supplier.name}.', 'success')
        
    db.session.commit()
    return redirect(url_for('suppliers.index'))
