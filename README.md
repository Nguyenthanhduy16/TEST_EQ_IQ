# Mini Test CLB HTHT - Web App nội bộ

App web nội bộ chạy bằng Flask + SQLite. Ứng viên mở form trên trình duyệt, nộp bài, hệ thống chấm điểm ẩn ngay và ban tuyển xem dashboard trong khu quản trị.

## Tính năng chính
- Form 50 câu trắc nghiệm + thông tin ứng viên
- Chấm theo 8 trục tích cực, 2 trục rủi ro, 4 chỉ số kỹ thuật
- Tự sinh mức phù hợp, hồ sơ ứng viên, cờ rủi ro, trọng tâm phỏng vấn
- Dashboard lọc nhanh ứng viên
- Trang chi tiết từng ứng viên
- Ghi chú phỏng vấn và xuất CSV

## Chạy local
```bash
pip install -r requirements.txt
python app.py
```

App chạy tại:
```text
http://127.0.0.1:5000
```

## Đăng nhập admin
Mặc định:
- mật khẩu admin: `admin123`

Bạn nên đổi bằng biến môi trường trước khi dùng thật:
```bash
set ADMIN_PASSWORD=mat-khau-moi
set SECRET_KEY=mot-secret-key-bat-ky
python app.py
```

Hoặc trên macOS/Linux:
```bash
export ADMIN_PASSWORD=mat-khau-moi
export SECRET_KEY=mot-secret-key-bat-ky
python app.py
```

## Cấu trúc chính
- `app.py`: route Flask + lưu SQLite
- `question_data.py`: 50 câu hỏi
- `scoring.py`: map điểm và tính điểm
- `rules.py`: sinh flags, fit level, profile
- `summarizer.py`: sinh nhận xét và câu hỏi phỏng vấn
- `templates/`: giao diện
- `static/styles.css`: CSS

## Gợi ý dùng nội bộ
- Cho ứng viên truy cập `/apply`
- Ban tuyển truy cập `/admin`
- Nếu chỉ dùng trên máy cá nhân: để `127.0.0.1`
- Nếu muốn máy khác trong cùng mạng truy cập: chạy app bằng host `0.0.0.0` và mở port trong firewall nếu cần
