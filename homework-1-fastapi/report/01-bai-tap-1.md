# Bài tập 1

Bài tập 1 đo hiệu năng của Web API ở các kịch bản truy xuất cơ sở dữ liệu
(search / read) dưới tải, dùng Locust.

## Thiết lập

Kịch bản load test nằm trong `load/locustfile.py`. Mỗi user ảo lặp lại một tập
các request read với `wait_time` ngẫu nhiên 0.5 tới 2.0 giây giữa hai lần, mô
phỏng người dùng duyệt trang. Trọng số (task weight) phản ánh tần suất thực tế:

- `GET /offerings?term_id=&page=1&size=20` (duyệt offering của học kỳ) - trọng số 3.
- `GET /offerings?search=a` (tìm kiếm theo title / code) - trọng số 2.
- `GET /offerings/{id}` (chi tiết một offering) - trọng số 2.
- `GET /students/{id}/enrollments` (transcript của một student) - trọng số 3.
- `GET /students/{id}/schedule?term_id=` (thời khóa biểu) - trọng số 1.
- `GET /courses?page=1&size=20` (danh sách course) - trọng số 1.

Các endpoint này được chọn vì đều chạm database và có độ nặng khác nhau: từ tra
cứu theo khóa chính (`/offerings/{id}`) tới truy vấn có join và đếm
(`/offerings` phải đếm số enrollment đang active để tính `available_seats`).

Chạy headless để lấy số liệu:

```bash
make up && make seed   # API tại :8000, dữ liệu seed sẵn
locust -f load/locustfile.py --host http://localhost:8000 \
       --users 50 --spawn-rate 10 --run-time 1m --headless
```

Thông số lần chạy: <!-- TODO: số users, spawn-rate, thời lượng, cấu hình máy -->

## Kết quả

<!-- TODO: điền số đo từ Locust (cột Aggregated và từng endpoint). -->

- `GET /offerings [browse term]`: RPS = ..., p50 = ... ms, p95 = ... ms, p99 = ... ms, failures = ...
- `GET /offerings [search]`: ...
- `GET /offerings/{id}`: ...
- `GET /students/{id}/enrollments`: ...
- `GET /students/{id}/schedule`: ...
- `GET /courses [list]`: ...
- Tổng hợp (Aggregated): ...

![Kết quả Locust (tab Statistics / Charts).](assets/locust.png)

## Phân tích

Một số điểm bám sát thiết kế của API, số đo thực tế dùng để kiểm chứng:

- **Framework async (FastAPI + asyncpg).** Các request ở đây đều I/O-bound (chờ
  DB). Với mô hình async, một event loop phục vụ được nhiều request đang chờ I/O
  cùng lúc, nên throughput ít bị giới hạn bởi số worker. Một framework sync (ví
  dụ Flask với driver đồng bộ) sẽ chiếm một worker trong suốt thời gian chờ DB,
  cần nhiều worker hơn để đạt cùng mức concurrency.
- **Độ nặng khác nhau giữa các endpoint.** `GET /offerings/{id}` chủ yếu là tra
  cứu theo primary key nên nhanh nhất. `GET /offerings` (list) nặng hơn vì có
  join sang `courses`/`terms` và một subquery đếm enrollment active để tính
  `available_seats`. Kỳ vọng p95 của list cao hơn của detail; số đo sẽ cho thấy
  chênh lệch này.
- **Pagination giới hạn payload.** `size=20` chặn kích thước kết quả, giữ latency
  ổn định khi dữ liệu lớn dần, thay vì trả toàn bộ bảng.
- **Index.** Các foreign key (`student_id`, `offering_id`, `term_id`,
  `course_id`) đều có index nên join và lọc nhanh. Ngược lại, `search` dùng
  `ILIKE '%...%'` trên `title`/`course_code` (không có index trigram) nên phải
  quét tuần tự, dự kiến là kịch bản đọc chậm nhất; đây là điểm có thể tối ưu.
- **N+1.** `GET /students/{id}/enrollments` dùng `selectinload` để nạp
  offering/course/term theo lô, tránh N+1 query.

<!-- TODO: đối chiếu các nhận định trên với số đo thực tế; nêu bottleneck quan
sát được và giải thích. So sánh với Flask là tùy chọn, chưa được triển khai. -->
