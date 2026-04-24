# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app
from app.extensions import db
from app.models.product import Category

app = create_app()

with app.app_context():
    descs = {
        'But cac loai': ('Bút các loại', 'Bút bi, bút gel, bút mực, bút lông, bút dạ - các loại bút phục vụ viết tay, ký hợp đồng và trang trí.'),
        'Giay & Tap':   ('Giấy & Tập',   'Giấy in A4, giấy photo, tập học sinh, vở kẻ ô - vật tư giấy thiết yếu cho văn phòng và học sinh.'),
        'Dung cu hoc tap': ('Dụng cụ học tập', 'Thước kẻ, tẩy, compa, kéo, dao rọc giấy - dụng cụ hỗ trợ học tập và làm việc hàng ngày.'),
        'Bia & File':   ('Bìa & File',   'Bìa còng, bìa kẹp, túi file, hộp đựng tài liệu - giải pháp lưu trữ và sắp xếp hồ sơ chuyên nghiệp.'),
    }

    all_cats = Category.query.all()
    updated = 0
    for cat in all_cats:
        for key, (vn_name, desc) in descs.items():
            if cat.name == vn_name:
                cat.description = desc
                updated += 1
                print(f'[OK] Updated: {cat.name}')
                break

    db.session.commit()
    print(f'\nDone: updated {updated} / {len(all_cats)} categories.')

    # Verify
    print('\nCurrent categories:')
    for cat in Category.query.all():
        prod_count = cat.products.count()
        desc_short = (cat.description[:50] + '...') if cat.description and len(cat.description) > 50 else (cat.description or '(no desc)')
        print(f'  [{cat.id}] {cat.name} | icon={cat.icon} | products={prod_count} | desc={desc_short}')
