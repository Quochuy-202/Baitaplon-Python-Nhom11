import os
from flask import Flask
from app.extensions import db, migrate, login_manager
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── Extensions ───────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    from app.extensions import csrf
    csrf.init_app(app)

    login_manager.login_view     = 'auth.login'
    login_manager.login_message  = 'Vui lòng đăng nhập để tiếp tục.'
    login_manager.login_message_category = 'warning'

    # ── Import tất cả models (để Alembic nhận diện) ──
    with app.app_context():
        from app.models import (
            User, Role, Product, Category, Unit, Barcode, StockMovement,
            Customer, Supplier, PurchaseOrder, PurchaseOrderItem,
            Order, OrderItem, CashTransaction,
            Promotion, PriceList, PriceListItem, AuditLog,
        )

    # ── Blueprints ────────────────────────────────────
    from app.blueprints.auth       import auth_bp
    from app.blueprints.dashboard  import dashboard_bp
    from app.blueprints.products   import products_bp
    from app.blueprints.storefront import storefront_bp
    from app.blueprints.inventory  import inventory_bp
    from app.blueprints.customers  import customers_bp
    from app.blueprints.suppliers  import suppliers_bp
    from app.blueprints.pos        import pos_bp
    from app.blueprints.cashflow   import cashflow_bp
    from app.blueprints.promotions import promotions_bp
    from app.blueprints.reports    import reports_bp
    from app.blueprints.settings   import settings_bp

    app.register_blueprint(storefront_bp, url_prefix='/')
    app.register_blueprint(auth_bp,       url_prefix='/auth')
    app.register_blueprint(dashboard_bp,  url_prefix='/dashboard')
    app.register_blueprint(products_bp,   url_prefix='/products')
    app.register_blueprint(inventory_bp,  url_prefix='/inventory')
    app.register_blueprint(customers_bp,  url_prefix='/customers')
    app.register_blueprint(suppliers_bp,  url_prefix='/suppliers')
    app.register_blueprint(pos_bp,        url_prefix='/pos')
    app.register_blueprint(cashflow_bp,   url_prefix='/cashflow')
    app.register_blueprint(promotions_bp, url_prefix='/promotions')
    app.register_blueprint(reports_bp,    url_prefix='/reports')
    app.register_blueprint(settings_bp,   url_prefix='/settings')

    # ── Tạo thư mục uploads nếu chưa có ──────────────
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ── Context processors ────────────────────────────
    @app.context_processor
    def inject_globals():
        from app.models.product import Product
        low_stock_count = Product.query.filter(
            Product.is_active == True,
            Product.stock_quantity <= Product.min_stock
        ).count()
        return {
            'store_name':    app.config.get('STORE_NAME', 'VPP Manager'),
            'store_address': app.config.get('STORE_ADDRESS', ''),
            'store_phone':   app.config.get('STORE_PHONE', ''),
            'store_email':   app.config.get('STORE_EMAIL', ''),
            'low_stock_count': low_stock_count,
        }

    # ── Jinja Globals ─────────────────────────────────
    app.jinja_env.globals.update(enumerate=enumerate)

    return app
