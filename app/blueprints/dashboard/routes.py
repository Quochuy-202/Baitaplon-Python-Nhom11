from flask import render_template
from flask_login import login_required
from datetime import datetime, timedelta
from sqlalchemy import func

from . import dashboard_bp
from app.extensions import db
from app.models import Order, Product, Customer

@dashboard_bp.route('/')
@login_required
def index():
    today = datetime.utcnow().date()
    
    # 1. Doanh thu hôm nay
    today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        db.func.date(Order.order_date) == today,
        Order.status == 'completed'
    ).scalar() or 0
    
    # 2. Tổng đơn hôm nay
    today_orders = Order.query.filter(
        db.func.date(Order.order_date) == today,
        Order.status == 'completed'
    ).count()
    
    # 3. Sản phẩm cảnh báo tồn kho
    low_stock_products = Product.query.filter(
        Product.is_active == True,
        Product.stock_quantity <= Product.min_stock
    ).all()
    count_low_stock = len(low_stock_products)
    
    # 4. Doanh thu 7 ngày qua (cho chart)
    seven_days_ago = today - timedelta(days=6)
    sales_data = db.session.query(
        db.func.date(Order.order_date).label('date'),
        func.sum(Order.total_amount).label('total')
    ).filter(
        db.func.date(Order.order_date) >= seven_days_ago,
        Order.status == 'completed'
    ).group_by(db.func.date(Order.order_date)).all()
    
    dates = []
    revenues = []
    # Điền các ngày trống
    for i in range(7):
        d = seven_days_ago + timedelta(days=i)
        dates.append(d.strftime('%d/%m'))
        found = next((item.total for item in sales_data if item.date == d), 0)
        revenues.append(float(found))

    # 5. Top 5 SP bán chạy tháng này
    start_of_month = today.replace(day=1)
    from app.models import OrderItem
    top_products = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label('qty')
    ).join(OrderItem.product).join(Order).filter(
        Order.status == 'completed',
        db.func.date(Order.order_date) >= start_of_month
    ).group_by(Product.id).order_by(db.text('qty DESC')).limit(5).all()

    return render_template('dashboard/index.html',
                           today_revenue=today_revenue,
                           today_orders=today_orders,
                           count_low_stock=count_low_stock,
                           dates=dates,
                           revenues=revenues,
                           top_products=top_products,
                           low_stock_products=low_stock_products[:5]) # chỉ show 5 SP trên widget
