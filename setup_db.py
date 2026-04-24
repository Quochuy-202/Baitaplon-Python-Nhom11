import pymysql
from app import create_app
from app.extensions import db
from app.models import User, Category, Unit, Product, Barcode, Role

def setup_mysql_db():
    # 1. Connect to create database if not exists
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS vanphongpham_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("--- Checked/Created database vanphongpham_db ---")
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        return

    # 2. Init tables using SQLAlchemy
    app = create_app()
    with app.app_context():
        try:
            db.create_all()
            print("--- Created all tables ---")
            
            # 3. Create Roles
            if not Role.query.first():
                roles = [
                    ('admin', 'Quan tri vien'),
                    ('thungan', 'Thu ngan'),
                    ('thukho', 'Thu kho')
                ]
                for r_name, d_name in roles:
                    db.session.add(Role(name=r_name, display_name=d_name))
                db.session.flush()
                print("--- Created basic roles ---")

            # 4. Create Admin User if not exists
            admin_role = Role.query.filter_by(name='admin').first()
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin = User(
                    username='admin',
                    password_hash='admin123', # Plain text
                    full_name='Admin User',
                    role_id=admin_role.id if admin_role else None,
                    is_active=True
                )
                db.session.add(admin)
                print("--- Created default admin user (admin / admin123) ---")
            else:
                # Update existing admin to plain text
                admin_user.password_hash = 'admin123'
                if admin_role: admin_user.role_id = admin_role.id
                print("--- Reset admin password to plain text ---")

            # 5. Create Units
            if not Unit.query.first():
                units = ['Cai', 'Bo', 'Quyen', 'Hop', 'Ram', 'Cay']
                for u_name in units:
                    db.session.add(Unit(name=u_name))
                print("--- Added basic units ---")

            # 6. Create Sample Categories
            if not Category.query.first():
                cats = [
                    ('But cac loai', 'fa-pen-nib', 'But bi, but gel, but ky cao cap...'),
                    ('Giay & Tap', 'fa-book', 'Giay in A4, vo hoc sinh, so tay...'),
                    ('Dung cu hoc tap', 'fa-ruler-combined', 'Thuoc, tay, compa, mau ve...'),
                    ('Bia & File', 'fa-folder-open', 'Bia cong, tui nhua, kep tai lieu...')
                ]
                for name, icon, desc in cats:
                    db.session.add(Category(name=name, icon=icon, description=desc))
                print("--- Added basic categories ---")

            db.session.commit()
            print("--- Database Setup Complete (Plain Text Passwords) ---")
            
        except Exception as e:
            print(f"Error initializing data: {e}")

if __name__ == "__main__":
    setup_mysql_db()
