from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
import uuid

from . import products_bp
from .forms import ProductForm, CategoryForm
from app.extensions import db
from app.models import Product, Category, Unit, Barcode, StockMovement
from app.models.product import generate_sku

# ... (các routes product cũ giữ nguyên) ...

# ── CATEGORIES MANAGEMENT ────────────────────────────────

@products_bp.route('/categories')
@login_required
def list_categories():
    categories = Category.query.all()
    return render_template('products/categories.html', categories=categories)

@products_bp.route('/categories/new', methods=['GET', 'POST'])
@login_required
def create_category():
    form = CategoryForm()
    # Populate parent choices
    form.parent_id.choices = [(0, '-- Không có --')] + [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            parent_id=form.parent_id.data if form.parent_id.data != 0 else None,
            description=form.description.data,
            icon=form.icon.data
        )
        db.session.add(category)
        db.session.commit()
        flash('Đã thêm danh mục mới.', 'success')
        return redirect(url_for('products.list_categories'))
        
    return render_template('products/category_form.html', form=form, title='Thêm Danh Mục Mới')

@products_bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    # Populate parent choices (loại trừ chính nó)
    form.parent_id.choices = [(0, '-- Không có --')] + [(c.id, c.name) for c in Category.query.filter(Category.id != id).all()]
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.parent_id = form.parent_id.data if form.parent_id.data != 0 else None
        category.description = form.description.data
        category.icon = form.icon.data
        db.session.commit()
        flash('Đã cập nhật danh mục.', 'success')
        return redirect(url_for('products.list_categories'))
        
    if not form.parent_id.data:
        form.parent_id.data = 0
        
    return render_template('products/category_form.html', form=form, title='Sửa Danh Mục')

@products_bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    if not current_user.has_role('admin'):
        flash('Bạn không có quyền thực hiện thao tác này.', 'danger')
        return redirect(url_for('products.list_categories'))
        
    category = Category.query.get_or_404(id)
    # Kiểm tra xem có sản phẩm nào thuộc danh mục này không
    if category.products.count() > 0:
        flash('Không thể xóa danh mục đang có sản phẩm.', 'warning')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Đã xóa danh mục.', 'success')
        
    return redirect(url_for('products.list_categories'))

@products_bp.route('/')
@login_required
def list_products():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q', '')
    cat_id = request.args.get('category_id', type=int)
    
    products_query = Product.query.filter_by(is_active=True)
    
    if query:
        products_query = products_query.filter(Product.name.ilike(f'%{query}%'))
    if cat_id:
        products_query = products_query.filter_by(category_id=cat_id)
        
    pagination = products_query.order_by(Product.id.desc()).paginate(page=page, per_page=15)
    categories = Category.query.all()
    
    return render_template('products/list.html', 
                           pagination=pagination, 
                           products=pagination.items,
                           categories=categories,
                           query=query,
                           cat_id=cat_id)

@products_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    form = ProductForm()
    # Populate choices
    form.category_id.choices = [(str(c.id), c.name) for c in Category.query.all()]
    form.unit_id.choices = [(str(u.id), u.name) for u in Unit.query.all()]
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            category_id=int(form.category_id.data),
            unit_id=int(form.unit_id.data),
            sku=form.sku.data or generate_sku(),
            description=form.description.data,
            cost_price=form.cost_price.data,
            retail_price=form.retail_price.data,
            wholesale_price=form.wholesale_price.data,
            stock_quantity=form.stock_quantity.data,
            min_stock=form.min_stock.data,
            max_stock=form.max_stock.data,
            location=form.location.data,
        )
        db.session.add(product)
        db.session.flush() # Lấy ID
        
        # Thêm mã vạch nếu có, hoặc tạo mới
        barcode_val = form.barcode.data
        if not barcode_val:
            barcode_val = f'BC{product.id:06d}' # barcode tự sinh
            
        bc = Barcode(product_id=product.id, barcode=barcode_val, is_primary=True)
        db.session.add(bc)
        
        # Tạo phiếu nhập kho ban đầu (nếu có số lượng > 0)
        if product.stock_quantity > 0:
            sm = StockMovement(
                product_id=product.id,
                user_id=current_user.id,
                movement_type='in',
                quantity=product.stock_quantity,
                reference_type='manual',
                notes='Tồn kho ban đầu'
            )
            db.session.add(sm)
            
        db.session.commit()
        flash('Đã thêm sản phẩm mới thành công.', 'success')
        return redirect(url_for('products.list_products'))
        
    return render_template('products/form.html', form=form, title='Thêm Sản Phẩm Mới')

@products_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    # Populate choices
    form.category_id.choices = [(str(c.id), c.name) for c in Category.query.all()]
    form.unit_id.choices = [(str(u.id), u.name) for u in Unit.query.all()]
    
    if request.method == 'GET':
        form.category_id.data = str(product.category_id)
        form.unit_id.data = str(product.unit_id)
        form.barcode.data = product.primary_barcode
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.category_id = int(form.category_id.data)
        product.unit_id = int(form.unit_id.data)
        product.sku = form.sku.data or product.sku
        product.description = form.description.data
        product.cost_price = form.cost_price.data
        product.retail_price = form.retail_price.data
        product.wholesale_price = form.wholesale_price.data
        product.stock_quantity = form.stock_quantity.data
        product.min_stock = form.min_stock.data
        product.max_stock = form.max_stock.data
        product.location = form.location.data
        
        # Cập nhật mã vạch chính
        if form.barcode.data:
            bc = Barcode.query.filter_by(product_id=product.id, is_primary=True).first()
            if bc:
                bc.barcode = form.barcode.data
            else:
                new_bc = Barcode(product_id=product.id, barcode=form.barcode.data, is_primary=True)
                db.session.add(new_bc)
                
        db.session.commit()
        flash('Đã cập nhật thông tin sản phẩm.', 'success')
        return redirect(url_for('products.list_products'))
        
    return render_template('products/form.html', form=form, title='Sửa Sản Phẩm')

@products_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    if not current_user.has_role('admin'):
        return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        
    product = Product.query.get_or_404(id)
    product.is_active = False # Soft delete
    db.session.commit()
    flash('Đã xóa sản phẩm.', 'success')
    return redirect(url_for('products.list_products'))

# API Cho POS Lookup
@products_bp.route('/api/lookup', methods=['POST'])
@login_required
def api_lookup():
    """ Tìm kiếm sản phẩm bằng mã vạch hoặc tên """
    data = request.get_json() or {}
    term = data.get('term', '').strip()
    
    if not term:
        return jsonify([])
        
    # Thử tìm theo mã vạch trước
    bc = Barcode.query.filter_by(barcode=term).first()
    if bc and bc.product.is_active:
        p = bc.product
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'price': float(p.retail_price),
            'stock': p.stock_quantity,
            'barcode': bc.barcode
        }])
        
    # Hoặc tìm theo tên / SKU
    products = Product.query.filter(
        Product.is_active == True,
        db.or_(
            Product.name.ilike(f'%{term}%'),
            Product.sku.ilike(f'%{term}%')
        )
    ).limit(10).all()
    
    results = []
    for p in products:
        results.append({
            'id': p.id,
            'name': p.name,
            'price': float(p.retail_price),
            'stock': p.stock_quantity,
            'barcode': p.primary_barcode
        })
        
    return jsonify(results)
