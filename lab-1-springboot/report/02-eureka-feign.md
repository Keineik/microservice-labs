# Vai trò của Eureka Server và lợi ích của việc gọi service theo tên

## Vai trò của Eureka Server

Eureka Server đóng vai trò service registry: một danh bạ trung tâm cho biết trong
hệ thống hiện có những service nào và mỗi service đang chạy ở đâu.

- **Đăng ký (register).** Khi khởi động, mỗi service (student-service,
  course-service, enrollment-service, web-client) tự đăng ký với Eureka Server
  bằng tên logic của nó (giá trị `spring.application.name`) kèm địa chỉ và port.
- **Gửi heartbeat (lease renewal).** Định kỳ, service gửi tín hiệu còn sống tới
  Eureka Server. Nếu một service ngừng gửi, Eureka Server sẽ loại nó khỏi danh
  bạ, nhờ đó danh bạ luôn phản ánh các instance đang thực sự hoạt động.
- **Khám phá (discover).** Bên gọi lấy về danh sách instance theo tên service từ
  Eureka Server, thay vì phải biết trước địa chỉ cụ thể.

Trong bài này, discovery-server được cấu hình `register-with-eureka: false` và
`fetch-registry: false` vì bản thân nó là registry, không cần đăng ký với chính
mình.

## Gọi service theo tên với OpenFeign

Các service không giữ địa chỉ URL của nhau. Thay vào đó, chúng khai báo một Feign
client trỏ tới tên service:

```java
@FeignClient(name = "course-service", path = "/api/courses")
public interface CourseClient {
    @GetMapping("/{courseCode}")
    CourseDto getByCode(@PathVariable String courseCode);
}
```

Ở đây chỉ có tên logic `course-service`, không có host hay port. Khi gọi, Spring
Cloud LoadBalancer sẽ hỏi Eureka Server để lấy một instance đang sống của
`course-service` rồi thực hiện lời gọi HTTP tới instance đó.

## Lợi ích của gọi theo tên so với URL cố định

- **Không phụ thuộc địa chỉ vật lý.** Instance có thể đổi host, đổi port, khởi
  động lại hay chạy trong container mà bên gọi không phải sửa cấu hình.
- **Cân bằng tải (load balancing).** Khi một service có nhiều instance, lời gọi
  được phân phối giữa các instance mà không cần thêm cấu hình ở bên gọi.
- **Co giãn linh hoạt (scaling).** Thêm hoặc bớt instance chỉ cần đăng ký hoặc
  hủy đăng ký với Eureka; danh bạ tự cập nhật.
- **Một nguồn sự thật duy nhất.** Vị trí của mỗi service được quản lý tập trung ở
  Eureka Server, tránh việc rải rác URL cố định khắp nơi trong mã nguồn.
- **Khả năng chịu lỗi tốt hơn.** Instance đã chết sẽ bị loại khỏi danh bạ, nên
  lời gọi hướng tới các instance còn sống.

## Xử lý lỗi khi gọi service

Lời gọi qua Feign được bọc bởi circuit breaker của Resilience4j, kèm timeout và
fallback:

- Nếu course-service không phản hồi, fallback trả về một placeholder chỉ chứa
  `courseCode`; dòng dữ liệu vẫn hiển thị và được đánh dấu là thiếu chi tiết.
- Nếu student-service không phản hồi, fallback trả về null; phần thông tin sinh
  viên bị lược bỏ nhưng danh sách học phần đã đăng ký vẫn hiển thị (vì dữ liệu này
  nằm trong cơ sở dữ liệu riêng của enrollment-service).
- Trường hợp student-service trả về lỗi 404 thật (sinh viên không tồn tại) được
  phân biệt với trường hợp service sập, nhờ fallback đọc được nguyên nhân lỗi.

Nhờ đó hệ thống suy giảm mềm (degrade) thay vì hỏng toàn bộ khi một service tạm
thời không sẵn sàng.
