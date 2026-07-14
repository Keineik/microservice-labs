# Tự đánh giá mức độ hoàn thành

## Mức độ hoàn thành theo yêu cầu

- **Bài tập 1 - đo hiệu năng bằng Locust**: đang thực hiện. Đã có kịch bản load
  test (`load/locustfile.py`) và phần trình bày phương pháp, phân tích (mục 1);
  còn thiếu số đo thực tế và phần so sánh với Flask, sẽ bổ sung sau.
- **Contract client/server (OpenAPI)**: hoàn thành. Pydantic schema sinh OpenAPI,
  xem mục 2.1.3 và `/docs`.
- **Ít nhất 2-3 bảng quan hệ, mỗi bảng hơn 100 dòng**: hoàn thành. 5 bảng nghiệp
  vụ + bảng idempotency, seed hơn 100 dòng ở students/courses/offerings/enrollments,
  xem mục 2.1.2 và `scripts/seed_data.py`.
- **Dependency Injection và so sánh có/không dùng**: hoàn thành. Xem mục 2.1.5 và
  `docs/di_vs_no_di.md`.
- **REST maturity level 2 và status code đúng chuẩn**: hoàn thành. Xem mục 2.1.6.
- **RFC 7807 cho lỗi**: hoàn thành. Xem mục 2.1.7 và `src/app/core/problems.py`.
- **Idempotency**: hoàn thành. Header `Idempotency-Key` ở `POST /enrollments`,
  xem mục 2.1.8 và `src/app/services/enrollment.py`.
- **API versioning**: hoàn thành. `/api/v1` và `/api/v2` phục vụ song song, xem
  mục 2.1.9 và `src/app/main.py`.
- **Bài tập 3 - ứng dụng web dùng API**: hoàn thành. Web client Jinja2 + HTMX,
  xem mục 2.2 và `src/web/`.

## Giới hạn và phần ngoài phạm vi

- **Authentication / authorization**: cố ý để dành cho bài tập sau; API nhận
  `student_id` tường minh (mục 2.1.1).
- **Thao tác admin** (quản lý catalog, thêm/xóa student): ngoài phạm vi, chỉ tạo
  bằng seed script (mục 2.1.1).
- **So sánh FastAPI với Flask** ở Bài tập 1: chưa triển khai; sẽ đo và so sánh
  sau.

## Kiến thức đã áp dụng

- SQLAlchemy 2.0 async + asyncpg; transaction và row lock (`FOR UPDATE`) để tránh
  overbook / double-book.
- Partial unique index để đảm bảo tính duy nhất của đăng ký đang active mà vẫn giữ
  lịch sử.
- Thiết kế REST, status code, và định dạng lỗi RFC 7807.
- Idempotency cho thao tác POST và API versioning theo path.
- Dependency Injection với FastAPI `Depends`, giúp test bằng cách override một
  provider.
- Alembic migration, seed dữ liệu bằng Faker, kiểm thử với pytest.
- Mô hình Backend-for-Frontend và HTMX cho web client, đóng gói bằng Docker Compose.
