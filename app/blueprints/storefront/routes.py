from flask import render_template
from . import storefront_bp
from app.models import Product, Category

@storefront_bp.route('/')
def index():
    categories = Category.query.all()
    # Hiển thị sản phẩm nổi bật / mới nhất trên trang chủ
    featured_products = Product.query.filter_by(is_active=True).order_by(Product.id.desc()).limit(8).all()
    
    return render_template('storefront/index.html', 
                         categories=categories,
                         featured_products=featured_products)
