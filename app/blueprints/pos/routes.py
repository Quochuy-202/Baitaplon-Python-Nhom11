from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import uuid

from . import pos_bp
from app.extensions import db
from app.models import Order, OrderItem, Product, Customer

@pos_bp.route('/')
@login_required
def index():
    # Render giao diện POS React/Vue/Vanilla JS tuỳ hỷ (mình dùng Vanilla JS cho đơn giản)
    return render_template('pos/index.html')


@pos_bp.route('/api/checkout', methods=['POST'])
@login_required
def checkout():
    data = request.get_json()
    items = data.get('items', [])
    payment_method = data.get('payment_method', 'cash')
    amount_paid = data.get('amount_paid', 0)
    customer_id = data.get('customer_id')
    
    if not items:
        return jsonify({'success': False, 'message': 'Giỏ hàng trống'}), 400
        
    try:
        # 1. Tạo Order
        order_code = f"HD{datetime.now().strftime('%y%m%d%H%M%S')}"
        new_order = Order(
            order_code=order_code,
            user_id=current_user.id,
            customer_id=customer_id,
            payment_method=payment_method,
            status='completed'
        )
        db.session.add(new_order)
        db.session.flush()
        
        # 2. Xử lý Order Items & Trừ tồn kho
        total_amount = 0
        for item in items:
            product_id = item['id']
            qty = int(item['quantity'])
            
            product = Product.query.get(product_id)
            if not product:
                continue
                
            price = float(product.retail_price)
            item_total = price * qty
            total_amount += item_total
            
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                product_name=product.name,
                quantity=qty,
                unit_price=price,
                total_price=item_total
            )
            db.session.add(order_item)
            
            # Giảm trừ tồn
            product.stock_quantity -= qty
            
            # (Có thể ghi StockMovement ở đây)
            
        new_order.subtotal = total_amount
        new_order.total_amount = total_amount
        new_order.paid_amount = float(amount_paid)
        new_order.change_amount = float(amount_paid) - total_amount
        
        # Đánh dấu point nếu có customer_id -> thực hiện ở service
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Thanh toán thành công',
            'order_id': new_order.id,
            'order_code': new_order.order_code
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
