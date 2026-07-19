# Vai trò của Eureka Server và lợi ích của việc gọi service theo tên

## Vai trò của Eureka Server

Eureka Server là service registry: một registry trung tâm cho biết hệ thống hiện
có những service nào và mỗi service đang chạy ở đâu.

- **Register.** Khi khởi động, mỗi service (student-service, course-service,
  enrollment-service, web-client) tự đăng ký với Eureka Server bằng tên logic của
  nó (`spring.application.name`) kèm địa chỉ và port.
- **Heartbeat (lease renewal).** Định kỳ, mỗi service gửi heartbeat báo còn sống.
  Nếu một service ngừng gửi, Eureka loại nó khỏi registry, nên registry luôn phản
  ánh các instance đang thực sự hoạt động.
- **Discover.** Bên gọi lấy danh sách instance theo tên service từ Eureka, thay
  vì phải biết trước địa chỉ cụ thể.

Trong bài này, discovery-server đặt `register-with-eureka: false` và
`fetch-registry: false` vì bản thân nó là registry, không cần đăng ký với chính
mình.

## Gọi service theo tên với OpenFeign

Các service không giữ URL của nhau. Thay vào đó, mỗi bên khai báo một Feign client
trỏ tới tên service:

```java
@FeignClient(name = "course-service", path = "/api/offerings")
public interface OfferingClient {
    @GetMapping("/{offeringCode}")
    OfferingDto getByCode(@PathVariable String offeringCode);
}
```

Ở đây chỉ có tên logic `course-service`, không có host hay port. Khi gọi, Spring
Cloud LoadBalancer hỏi Eureka để lấy một instance đang sống của `course-service`
rồi thực hiện lời gọi HTTP tới instance đó.

## Lợi ích của gọi theo tên so với URL cố định

- **Không phụ thuộc địa chỉ vật lý.** Instance có thể đổi host, đổi port, restart
  hay chạy trong container mà bên gọi không phải sửa cấu hình.
- **Load balancing.** Khi một service có nhiều instance, lời gọi được phân phối
  giữa các instance mà không cần cấu hình thêm ở phía gọi.
- **Scaling.** Thêm hoặc bớt instance chỉ cần register hoặc bỏ đăng ký với Eureka;
  registry tự cập nhật.
- **Single source of truth.** Vị trí của mỗi service được quản lý tập trung ở
  Eureka, tránh việc URL cố định nằm rải rác khắp mã nguồn.
- **Fault tolerance.** Instance đã chết bị loại khỏi registry, nên lời gọi chỉ
  hướng tới các instance còn sống.

## Xử lý lỗi khi gọi service

Lời gọi Feign được bọc bởi circuit breaker của Resilience4j, kèm timeout và
fallback:

- Nếu course-service không phản hồi, fallback trả về một placeholder suy ra từ
  `offeringCode`; dòng dữ liệu vẫn hiển thị và được đánh dấu là thiếu chi tiết.
- Nếu student-service không phản hồi, fallback trả về null; phần thông tin sinh
  viên bị lược bỏ nhưng danh sách học phần vẫn hiển thị (vì dữ liệu này nằm trong
  database riêng của enrollment-service).
- Lỗi 404 thật (sinh viên không tồn tại) được phân biệt với trường hợp service
  sập, nhờ fallback đọc được nguyên nhân (cause) của lỗi.

Nhờ đó hệ thống degrade (graceful degradation) thay vì hỏng toàn bộ khi một
service tạm thời không sẵn sàng.
