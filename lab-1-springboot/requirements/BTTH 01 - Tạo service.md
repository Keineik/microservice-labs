### **BÀI TẬP THỰC HÀNH #1: Xây dựng ứng dụng Microservice cơ bản**

**Mục tiêu:** Sau bài thực hành, sinh viên có thể xây dựng một hệ thống Microservice đơn giản sử dụng Spring Boot, Eureka Server và OpenFeign; đồng thời hiểu được cách các service đăng ký, khám phá và giao tiếp với nhau.

#### **1. Yêu cầu**
Dựa trên nội dung trong tài liệu hướng dẫn, xây dựng một hệ thống quản lý đăng ký học phần gồm các thành phần sau:
*   **Discovery Server** (Eureka Server).
*   **Student Service:** quản lý thông tin sinh viên.
*   **Course Service:** quản lý danh sách học phần.
*   **Enrollment Service:** quản lý thông tin đăng ký học phần của sinh viên.
*   **Web Client:** giao diện web hiển thị kết quả.

**Lưu ý:** Mỗi service phải chạy độc lập, đăng ký với Eureka Server và giao tiếp thông qua tên service (không sử dụng địa chỉ URL cố định).

#### **2. Chức năng tối thiểu**
*   **Student Service:** xem danh sách sinh viên, xem chi tiết một sinh viên, thêm mới sinh viên.
*   **Course Service:** xem danh sách học phần, xem chi tiết một học phần.
*   **Enrollment Service:** trả về thông tin đăng ký học phần của một sinh viên bằng cách gọi Student Service và Course Service.
*   **Web Client:** hiển thị thông tin sinh viên và các học phần đã đăng ký.

#### **3. Yêu cầu báo cáo**
Trong báo cáo, sinh viên trình bày ngắn gọn các nội dung sau:
*   Kiến trúc tổng thể của hệ thống (vẽ sơ đồ các service và mối quan hệ).
*   Vai trò của Eureka Server trong hệ thống.
*   Lợi ích của việc gọi service theo tên thay vì sử dụng URL cố định.
*   Mô tả luồng xử lý khi người dùng truy cập chức năng xem thông tin đăng ký học phần.

#### **4. Nội dung nộp**
*   Source code của toàn bộ hệ thống.
*   File báo cáo (PDF hoặc Word).
*   Ảnh chụp Eureka Dashboard hiển thị các service đã đăng ký.
*   Ảnh minh họa kết quả chạy Web Client.

#### **5. Thang điểm**
| Tiêu chí | Điểm |
| :--- | :--- |
| Hoàn thành Discovery Server và các service | 2.0 |
| Xây dựng đầy đủ các chức năng yêu cầu | 3.0 |
| Các service giao tiếp đúng thông qua Eureka/OpenFeign | 2.0 |
| Báo cáo trình bày rõ kiến trúc và luồng xử lý | 2.0 |
| Trình bày, tổ chức mã nguồn và minh chứng kết quả | 1.0 |

**Lưu ý:** Sinh viên được khuyến khích tham khảo tài liệu, công cụ hỗ trợ và AI trong quá trình học tập. Tuy nhiên, khi bảo vệ bài làm cần giải thích được kiến trúc hệ thống, chức năng của từng service và luồng xử lý của chương trình.