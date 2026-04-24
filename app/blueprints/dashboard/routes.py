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
    # Sử dụng datetime.now() để lấy giờ địa phương chính xác
    today = datetime.now().date()
    
    # 1. Doanh thu hôm nay
    today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        func.date(Order.order_date) == today,
        Order.status == 'completed'
    ).scalar() or 0
    
    # 2. Tổng đơn hôm nay
    today_orders = Order.query.filter(
        func.date(Order.order_date) == today,
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
    
    # Lấy dữ liệu thực tế từ DB
    sales_data = db.session.query(
        func.date(Order.order_date).label('date'),
        func.sum(Order.total_amount).label('total')
    ).filter(
        func.date(Order.order_date) >= seven_days_ago,
        Order.status == 'completed'
    ).group_by(func.date(Order.order_date)).all()
    
    # Chuyển kết quả truy vấn thành dictionary để dễ tra cứu
    sales_dict = {str(item.date): item.total for item in sales_data}
    
    dates = []
    revenues = []
    # Điền đầy đủ 7 ngày, kể cả ngày không có doanh thu
    for i in range(7):
        d = seven_days_ago + timedelta(days=i)
        dates.append(d.strftime('%d/%m'))
        # Tra cứu doanh thu trong dictionary, nếu không có thì bằng 0
        found = sales_dict.get(str(d), 0)
        revenues.append(float(found))

    # 5. Top 5 SP bán chạy tháng này
    start_of_month = today.replace(day=1)
    from app.models import OrderItem
    top_products = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label('qty')
    ).join(OrderItem, Product.id == OrderItem.product_id)\
     .join(Order, Order.id == OrderItem.order_id)\
     .filter(
        Order.status == 'completed',
        func.date(Order.order_date) >= start_of_month
    ).group_by(Product.id).order_by(db.desc('qty')).limit(5).all()

    return render_template('dashboard/index.html',
                           today_revenue=today_revenue,
                           today_orders=today_orders,
                           count_low_stock=count_low_stock,
                           dates=dates,
                           revenues=revenues,
                           top_products=top_products,
                           low_stock_products=low_stock_products[:5])
