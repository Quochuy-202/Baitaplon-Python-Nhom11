import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ──────────────────────────────
    # Security
    # ──────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vanphongpham-dev-secret-2025'

    # ──────────────────────────────
    # Database — MySQL qua Laragon
    # ──────────────────────────────
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or
        'mysql+pymysql://root:@localhost:3306/vanphongpham_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'connect_args': {
            'charset': 'utf8mb4',
        }
    }

    # ──────────────────────────────
    # Uploads
    # ──────────────────────────────
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # ──────────────────────────────
    # Store Info (fallback tới .env)
    # ──────────────────────────────
    STORE_NAME    = os.environ.get('STORE_NAME', 'Văn Phòng Phẩm ABC')
    STORE_ADDRESS = os.environ.get('STORE_ADDRESS', '123 Nguyễn Huệ, TP.HCM')
    STORE_PHONE   = os.environ.get('STORE_PHONE', '0901234567')
    STORE_EMAIL   = os.environ.get('STORE_EMAIL', 'vpp.abc@gmail.com')

    # ──────────────────────────────
    # Business Rules
    # ──────────────────────────────
    LOW_STOCK_THRESHOLD = 10   # Ngưỡng cảnh báo tồn kho thấp mặc định
    POINTS_PER_VND      = 100  # Chi 100 VND được 1 điểm
    GOLD_CARD_POINTS    = 5000
    SILVER_CARD_POINTS  = 2000
