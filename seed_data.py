import os
from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models import Role, User, Category, Unit, Product, Barcode

app = create_app()

def seed():
    with app.app_context():
        # Kiểm tra nếu DB đã có data thì bỏ qua
        if Role.query.first():
            print("Database already seeded!")
            return

        print("Seeding Roles...")
        r_admin = Role(name='admin', display_name='Quản trị viên')
        r_thungan = Role(name='thungan', display_name='Thu ngân')
        r_thukho = Role(name='thukho', display_name='Thủ kho')
        db.session.add_all([r_admin, r_thungan, r_thukho])
        db.session.flush()

        print("Seeding Users...")
        u_admin = User(username='admin', password_hash=generate_password_hash('admin123'), full_name='Chủ Cửa Hàng', role_id=r_admin.id)
        u_thungan = User(username='thungan', password_hash=generate_password_hash('123456'), full_name='Trần Thu Ngân', role_id=r_thungan.id)
        u_thukho = User(username='thukho', password_hash=generate_password_hash('123456'), full_name='Lê Thủ Kho', role_id=r_thukho.id)
        db.session.add_all([u_admin, u_thungan, u_thukho])

        print("Seeding Units...")
        unit_c = Unit(name='Chiếc', abbreviation='c')
        unit_b = Unit(name='Bút', abbreviation='b')
        unit_r = Unit(name='Ram', abbreviation='rm')
        unit_q = Unit(name='Quyển', abbreviation='q')
        unit_box = Unit(name='Hộp', abbreviation='hp')
        db.session.add_all([unit_c, unit_b, unit_r, unit_q, unit_box])
        db.session.flush()

        print("Seeding Categories...")
        cat_but = Category(name='Bút các loại', icon='fa-pen')
        cat_giay = Category(name='Giấy & Tập', icon='fa-copy')
        cat_dungcu = Category(name='Dụng cụ học tập', icon='fa-ruler')
        cat_file = Category(name='Bìa & File', icon='fa-folder-open')
        db.session.add_all([cat_but, cat_giay, cat_dungcu, cat_file])
        db.session.flush()

        print("Seeding Products...")
        products_data = [
            (cat_but.id, unit_b.id, 'Bút Bi Thiên Long TL-027 (Xanh)', 3000, 5000, 100),
            (cat_but.id, unit_b.id, 'Bút Gel Hồng Hà 123 (Đen)', 4500, 7000, 50),
            (cat_giay.id, unit_r.id, 'Giấy A4 Double A 80gsm', 65000, 80000, 20),
            (cat_giay.id, unit_r.id, 'Giấy A4 IK Plus 70gsm', 55000, 68000, 30),
            (cat_giay.id, unit_q.id, 'Vở Campus 96 trang', 8000, 12000, 150),
            (cat_dungcu.id, unit_c.id, 'Tẩy Pentel Ain', 12000, 18000, 40),
            (cat_dungcu.id, unit_c.id, 'Thước kẻ nhựa 20cm', 2500, 5000, 200),
            (cat_file.id, unit_box.id, 'Bìa còng Thiên Long 7cm', 25000, 35000, 15),
        ]

        for i, data in enumerate(products_data):
            p = Product(
                category_id=data[0],
                unit_id=data[1],
                name=data[2],
                sku=f'VPP-{1000+i}',
                cost_price=data[3],
                retail_price=data[4],
                stock_quantity=data[5]
            )
            db.session.add(p)
            db.session.flush()
            
            # Add barcode
            bc = Barcode(product_id=p.id, barcode=f'893{10000+i}', is_primary=True)
            db.session.add(bc)

        db.session.commit()
        print("Data seeded successfully!")

if __name__ == '__main__':
    seed()
