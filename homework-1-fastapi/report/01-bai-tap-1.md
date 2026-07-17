# Bài tập 1

Bài tập 1 so sánh hiệu năng giữa **sync** (Flask, WSGI) và **async** (FastAPI,
ASGI) trên các truy vấn đọc chạm cơ sở dữ liệu, và dùng Locust để chứng minh
tác động của concurrency model tới throughput và latency.

## Thiết kế thí nghiệm

Để cô lập đúng biến "sync so với async", chúng tôi dựng **hai app tối thiểu song
song** trong thư mục `benchmark/`, expose cùng các endpoint:

- **async**: FastAPI + async SQLAlchemy + asyncpg, chạy bằng uvicorn (một event
  loop).
- **sync**: Flask + sync SQLAlchemy + psycopg2, chạy bằng gunicorn sync worker.

Cả hai import chung `bench_common.py` (cùng câu lệnh SQL và cùng cách
serialization), nên payload giống hệt nhau. Những thứ được **giữ cố định** để so
sánh công bằng:

- Cùng PostgreSQL, cùng dữ liệu seed, cùng SQL, cùng index.
- Cùng connection pool size (mặc định 10, `max_overflow=0`) ở cả hai app.
- Cùng payload JSON (chung serializer).
- Cùng máy; warm up trước khi đo; chạy lặp lại vài lần.

Chỉ có **concurrency model** thay đổi.

Ghi chú về ORM: **SQLAlchemy mặc định là sync**, phần async là tùy chọn và cần
async driver (asyncpg). Dùng async SQLAlchemy bên trong Flask cũng không giúp
được, vì Flask (WSGI) vẫn xử lý blocking từng request trên mỗi worker; không có
event loop dùng chung. Vì vậy contender sync đúng nghĩa là Flask + psycopg2, còn
contender async là FastAPI + asyncpg.

## Kịch bản và cách chạy

Hai loại kịch bản (chọn bằng tag của Locust):

- **read**: các endpoint đọc thật (browse/search offering, chi tiết offering,
  transcript của student, danh sách course). Truy vấn nhanh (sub-millisecond).
- **io**: endpoint `/io` chạy `SELECT pg_sleep(...)` với thời gian mặc định
  **300 ms** (chỉnh qua `BENCH_IO_SECONDS` hoặc `?seconds=`). Kịch bản này cố ý
  làm request bị chờ ở DB để cô lập và phóng đại hiệu ứng sync/async.

Ma trận đo: `async-1w` (một tiến trình) so với `sync-1w` (một worker) và
`sync-4w` (bốn worker); mỗi cấu hình chạy cả `read` và `io`. Locust dùng
`-u 100 -r 20 -t 60s`, `wait_time = 0` (mỗi user gửi liên tục để đo throughput
ở trạng thái bão hòa).

Cách chạy (chi tiết ở `benchmark/README.md`):

```bash
uv sync --extra bench           # flask, gunicorn, psycopg2, locust
make bench-async                # FastAPI (async) :9001
make bench-sync                 # Flask (sync), 1 worker :9002
make bench-load HOST=http://localhost:9001 NAME=async-io   TAGS=io USERS=100 TIME=60s
make bench-load HOST=http://localhost:9002 NAME=sync-1w-io TAGS=io USERS=100 TIME=60s
```

## Kết quả

<!-- TODO: điền số đo thực tế từ benchmark/results/*_stats.csv (dòng Aggregated). -->

Kịch bản io (pg_sleep 300 ms):

- `async-io` (1 tiến trình): RPS = ..., p50 = ... ms, p95 = ... ms, failures = ...
- `sync-1w-io`: RPS = ..., p50 = ... ms, p95 = ... ms, failures = ...
- `sync-4w-io`: RPS = ..., p50 = ... ms, p95 = ... ms, failures = ...

Kịch bản read (truy vấn nhanh):

- `async-read`: ...
- `sync-1w-read`: ...
- `sync-4w-read`: ...

Kỳ vọng ở kịch bản io với pool 10 và sleep 300 ms: async một tiến trình giữ được
khoảng 10 request (giới hạn pool) chạy song song nên đạt xấp xỉ 10 / 0.3 ≈ 33
RPS; sync một worker chỉ xử lý một request 300 ms tại một thời điểm nên xấp xỉ
1 / 0.3 ≈ 3 RPS (chênh khoảng 10 lần). sync bốn worker nâng lên xấp xỉ 12 RPS,
tức sync cần nhiều worker/tiến trình để bằng những gì async làm trong một loop.
Số đo thực tế dùng để xác nhận các con số này.

## Phân tích

- **Cơ chế**: một sync worker block trong suốt round-trip tới DB, nên throughput
  xấp xỉ `1 / latency`; muốn phục vụ N request I/O song song thì cần khoảng N
  worker (tốn bộ nhớ, thêm tiến trình). Một async worker overlap nhiều round-trip
  trên cùng một event loop, đạt xấp xỉ `concurrency / latency` cho tới giới hạn
  pool, chỉ trong một tiến trình.
- **Bottleneck**: ở kịch bản io, DB latency chiếm ưu thế nên khác biệt rất rõ. Ở
  kịch bản read, truy vấn nhanh và pool/DB dễ trở thành giới hạn, nên khoảng cách
  thu hẹp lại; đây là điểm cần trung thực khi kết luận.
- **Sắc thái GIL**: psycopg2 nhả GIL trong lúc chờ I/O mạng, nên Flask nhiều
  worker/thread cũng overlap được I/O; lợi thế thật của async là làm điều đó
  trong một thread với chi phí bộ nhớ và context-switch thấp hơn nhiều, và mở
  rộng tới hàng nghìn kết nối đồng thời.
- **Khi nào async không thắng**: với tác vụ CPU-bound, async không giúp gì; và
  khi DB là bottleneck thì cả hai đều bị chặn như nhau.

<!-- TODO: đối chiếu số đo với các nhận định trên; nêu bottleneck quan sát được.
So sánh sâu hơn (ví dụ quét số users để vẽ throughput theo concurrency) là tùy
chọn. -->
