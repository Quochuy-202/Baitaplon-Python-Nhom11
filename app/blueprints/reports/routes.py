from flask import render_template, request
from flask_login import login_required
from . import reports_bp
from app.models import Order, OrderItem, Product
from app.extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func

@reports_bp.route('/')
@login_required
def index():
    # Thống kê tổng quan
    today = datetime.now().date()
    start_of_month = today.replace(day=1)
    
    # 1. Doanh thu hôm nay
    today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        func.date(Order.order_date) == today,
        Order.status == 'completed'
    ).scalar() or 0
    
    # 2. Doanh thu tháng này
    month_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        Order.order_date >= start_of_month,
        Order.status == 'completed'
    ).scalar() or 0
    
    # 3. Số đơn hàng hôm nay
    today_orders = Order.query.filter(
        func.date(Order.order_date) == today,
        Order.status == 'completed'
    ).count()

    # 4. Top 5 sản phẩm bán chạy (dựa trên số lượng)
    top_products = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label('total_qty')
    ).join(OrderItem, Product.id == OrderItem.product_id)\
     .join(Order, Order.id == OrderItem.order_id)\
     .filter(Order.status == 'completed')\
     .group_by(Product.id).order_by(db.desc('total_qty')).limit(5).all()
    
    # 5. Dữ liệu biểu đồ doanh thu 7 ngày gần nhất
    last_7_days = []
    revenue_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        rev = db.session.query(func.sum(Order.total_amount)).filter(
            func.date(Order.order_date) == day,
            Order.status == 'completed'
        ).scalar() or 0
        last_7_days.append(day.strftime('%d/%m'))
        revenue_data.append(float(rev))

    # 6. Lợi nhuận ước tính (Giả sử Lợi nhuận = Doanh thu - (Số lượng * Giá vốn))
    # Chúng ta tính sơ bộ lợi nhuận hôm nay
    profit_today = db.session.query(
        func.sum(OrderItem.total_price - (OrderItem.quantity * Product.cost_price))
    ).join(Product, Product.id == OrderItem.product_id)\
     .join(Order, Order.id == OrderItem.order_id)\
     .filter(func.date(Order.order_date) == today, Order.status == 'completed')\
     .scalar() or 0

    return render_template('reports/index.html',
                           today_revenue=today_revenue,
                           month_revenue=month_revenue,
                           today_orders=today_orders,
                           profit_today=profit_today,
                           top_products=top_products,
                           chart_labels=last_7_days,
                           chart_data=revenue_data)
