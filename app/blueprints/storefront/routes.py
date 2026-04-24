from flask import render_template, request
from . import storefront_bp
from app.models import Product, Category

@storefront_bp.route('/')
def index():
    categories = Category.query.all()
    q        = request.args.get('q', '').strip()
    cat_id   = request.args.get('cat', type=int)

    products_query = Product.query.filter_by(is_active=True)
    if q:
        products_query = products_query.filter(Product.name.ilike(f'%{q}%'))
    if cat_id:
        products_query = products_query.filter_by(category_id=cat_id)

    featured_products = products_query.order_by(Product.id.desc()).limit(8).all()

    # Config store từ env/default
    from flask import current_app
    store_name    = current_app.config.get('STORE_NAME',    'Văn Phòng Phẩm ABC')
    store_address = current_app.config.get('STORE_ADDRESS', '123 Nguyễn Huệ, TP.HCM')
    store_phone   = current_app.config.get('STORE_PHONE',   '028 1234 5678')
    store_email   = current_app.config.get('STORE_EMAIL',   'info@vpp-abc.vn')

    return render_template('storefront/index.html',
                           categories=categories,
                           featured_products=featured_products,
                           q=q,
                           active_cat=cat_id,
                           store_name=store_name,
                           store_address=store_address,
                           store_phone=store_phone,
                           store_email=store_email)
