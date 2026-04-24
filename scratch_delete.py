from app import create_app
from app.extensions import db
from app.models import Supplier

app = create_app()
with app.app_context():
    s = Supplier.query.get(1)
    if s:
        print(f"Found supplier: {s.name}, Active: {s.is_active}")
        s.is_active = False
        try:
            db.session.commit()
            print("Soft delete committed.")
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()
    else:
        print("Supplier not found.")
