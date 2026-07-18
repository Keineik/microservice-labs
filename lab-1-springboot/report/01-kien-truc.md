# Kiến trúc tổng thể

Hệ thống quản lý đăng ký học phần được xây dựng theo kiến trúc microservice, gồm
một Discovery Server (Eureka Server) và bốn service độc lập. Mỗi service chạy
riêng, có cơ sở dữ liệu riêng, đăng ký với Eureka Server và gọi nhau thông qua
tên service (service name) chứ không dùng địa chỉ URL cố định.

## Các thành phần

- **discovery-server** (port 8761, không dùng cơ sở dữ liệu): Eureka Server, nơi
  các service đăng ký và khám phá lẫn nhau.
- **student-service** (port 8081, H2 riêng): quản lý thông tin sinh viên.
- **course-service** (port 8082, H2 riêng): quản lý danh sách học phần.
- **enrollment-service** (port 8083, H2 riêng): quản lý đăng ký học phần; tổng
  hợp dữ liệu bằng cách gọi student-service và course-service.
- **web-client** (port 8080, không dùng cơ sở dữ liệu): giao diện web (Thymeleaf)
  hiển thị kết quả.

## Sơ đồ kiến trúc

```mermaid
flowchart TD
    browser["Trình duyệt"] --> web["web-client (:8080)"]

    subgraph registry["Service registry"]
        eureka["discovery-server\nEureka Server (:8761)"]
    end

    web -->|Feign, gọi theo tên| student["student-service (:8081)"]
    web -->|Feign, gọi theo tên| enroll["enrollment-service (:8083)"]
    enroll -->|Feign, gọi theo tên| student
    enroll -->|Feign, gọi theo tên| course["course-service (:8082)"]

    student -.->|register / heartbeat| eureka
    course -.->|register / heartbeat| eureka
    enroll -.->|register / heartbeat| eureka
    web -.->|register / fetch registry| eureka
```

Đường nét liền là lời gọi HTTP giữa các service (qua OpenFeign). Đường nét đứt là
tương tác với Eureka Server (đăng ký, gửi heartbeat, và lấy danh sách service).

## Nguyên tắc thiết kế

- **Mỗi service sở hữu dữ liệu của riêng mình (no shared database).** Không có
  bảng dùng chung, không có truy vấn join xuyên service. Đây là ranh giới khiến
  các thành phần trở thành service thực sự thay vì các module trong một ứng dụng.
- **Tham chiếu bằng business key.** enrollment-service chỉ lưu `studentCode` và
  `courseCode` trong mỗi bản ghi đăng ký, không lưu bản sao họ tên hay tên học
  phần. Khi cần hiển thị chi tiết, nó gọi student-service và course-service để
  lấy dữ liệu tại thời điểm đọc.
- **Hợp đồng (contract) tách rời.** Mỗi service tự định nghĩa DTO của mình; bên
  gọi (consumer) chỉ khai báo các trường nó cần. Không dùng thư viện DTO chung để
  tránh ràng buộc chặt giữa các service ở mức biên dịch.
- **web-client không có cơ sở dữ liệu.** Nó chỉ đọc dữ liệu từ các service khác
  qua Feign và kết xuất HTML.

## Công nghệ sử dụng

- Java 17, Spring Boot 4.1.0, Spring Cloud 2025.1.2 (Oakwood).
- Spring Cloud Netflix Eureka cho service discovery.
- Spring Cloud OpenFeign cho lời gọi giữa các service.
- Resilience4j (circuit breaker + fallback) cho xử lý lỗi.
- H2 in-memory cho lưu trữ của từng service; Thymeleaf cho giao diện web.
