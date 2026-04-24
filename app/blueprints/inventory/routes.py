from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import inventory_bp
from .forms import StockAdjustmentForm
from app.extensions import db
from app.models import Product, StockMovement, Category, Supplier, PurchaseOrder, PurchaseOrderItem
from datetime import datetime

@inventory_bp.route('/')
@login_required
def index():
    q = request.args.get('q', '')
    cat_id = request.args.get('category_id', type=int)
    
    products_query = Product.query.filter_by(is_active=True)
    if q:
        products_query = products_query.filter(Product.name.ilike(f'%{q}%'))
    if cat_id:
        products_query = products_query.filter_by(category_id=cat_id)
        
    products = products_query.order_by(Product.stock_quantity.asc()).all()
    categories = Category.query.all()
    
    # Statistics
    total_items = sum(p.stock_quantity for p in products)
    low_stock_items = [p for p in products if p.is_low_stock]
    
    return render_template('inventory/index.html', 
                           products=products, 
                           categories=categories,
                           total_items=total_items,
                           low_stock_count=len(low_stock_items),
                           q=q, cat_id=cat_id)

@inventory_bp.route('/movements')
@login_required
def movements():
    page = request.args.get('page', 1, type=int)
    movements = StockMovement.query.order_by(StockMovement.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('inventory/movements.html', pagination=movements, movements=movements.items)

@inventory_bp.route('/adjust', methods=['GET', 'POST'])
@login_required
def adjust():
    form = StockAdjustmentForm()
    # Populate products
    form.product_id.choices = [(p.id, f"{p.name} (Hiện có: {p.stock_quantity})") for p in Product.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        product = Product.query.get(form.product_id.data)
        qty = form.quantity.data
        m_type = form.movement_type.data
        
        # Update product stock
        if m_type == 'in':
            product.stock_quantity += qty
        else:
            if product.stock_quantity < qty:
                flash(f'Lỗi: Số lượng xuất ({qty}) lớn hơn tồn kho hiện tại ({product.stock_quantity}).', 'danger')
                return render_template('inventory/adjust_form.html', form=form)
            product.stock_quantity -= qty
            
        # Log movement
        movement = StockMovement(
            product_id=product.id,
            user_id=current_user.id,
            movement_type=m_type,
            quantity=qty,
            reference_type='manual',
            notes=form.notes.data
        )
        db.session.add(movement)
        db.session.commit()
        
        flash(f'Đã điều chỉnh kho cho sản phẩm: {product.name}', 'success')
        return redirect(url_for('inventory.index'))
        
    return render_template('inventory/adjust_form.html', form=form)

@inventory_bp.route('/purchase-orders')
@login_required
def list_purchase_orders():
    orders = PurchaseOrder.query.order_by(PurchaseOrder.order_date.desc()).all()
    return render_template('inventory/purchase_order_list.html', orders=orders)

@inventory_bp.route('/purchase-orders/new', methods=['GET', 'POST'])
@login_required
def create_purchase_order():
    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id')
        paid_amount = float(request.form.get('paid_amount', 0) or 0)
        notes = request.form.get('notes')
        
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            flash('Nhà cung cấp không hợp lệ.', 'danger')
            return redirect(url_for('inventory.create_purchase_order'))
            
        # Create Purchase Order
        order_code = f"PN{datetime.now().strftime('%y%m%d%H%M%S')}"
        new_order = PurchaseOrder(
            order_code=order_code,
            supplier_id=supplier.id,
            user_id=current_user.id,
            paid_amount=paid_amount,
            notes=notes,
            status='received'
        )
        db.session.add(new_order)
        db.session.flush()
        
        total_order_amount = 0
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('price[]')
        
        for i in range(len(product_ids)):
            p_id = product_ids[i]
            qty = int(quantities[i])
            price = float(prices[i])
            total_item = qty * price
            total_order_amount += total_item
            
            item = PurchaseOrderItem(
                purchase_order_id=new_order.id,
                product_id=p_id,
                quantity=qty,
                unit_price=price,
                total_price=total_item
            )
            db.session.add(item)
            
            product = Product.query.get(p_id)
            if product:
                product.stock_quantity += qty
                move = StockMovement(
                    product_id=product.id,
                    user_id=current_user.id,
                    movement_type='in',
                    quantity=qty,
                    reference_type='purchase_order',
                    reference_id=new_order.id,
                    notes=f'Nhập hàng từ {supplier.name}'
                )
                db.session.add(move)
        
        new_order.total_amount = total_order_amount
        debt_increase = total_order_amount - paid_amount
        if debt_increase > 0:
            supplier.debt_amount = (supplier.debt_amount or 0) + debt_increase
            
        db.session.commit()
        flash(f'Đã nhập hàng thành công. Mã phiếu: {order_code}', 'success')
        return redirect(url_for('inventory.list_purchase_orders'))
        
    suppliers = Supplier.query.filter_by(is_active=True).all()
    products = Product.query.filter_by(is_active=True).all()
    return render_template('inventory/purchase_order_form.html', suppliers=suppliers, products=products)
