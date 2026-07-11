### **BÀI TẬP CHƯƠNG 2 & 3**

**Thời gian thực hiện:** 2 tuần

#### **1. Nội dung các bài tập**

*   **Bài tập 1: Xây dựng và đo hiệu năng của web API**
    *   Xây dựng API ở những kịch bản kỹ thuật khác nhau, có thực hiện truy xuất cơ sở dữ liệu (tìm kiếm, đọc).
    *   So sánh hiệu năng của những kỹ thuật triển khai (implement) khác nhau như: **FastAPI**, **Flask**, v.v..
*   **Bài tập 2: Xây dựng và sử dụng Web API dùng FastAPI đúng chuẩn**
    *   API phải thiết lập **Contract giữa client và server**.
    *   Cơ sở dữ liệu phải có ít nhất **2–3 bảng có quan hệ** với nhau (ví dụ: users ↔ orders ↔ products).
    *   Mỗi bảng dữ liệu phải có ít nhất **100 dòng dữ liệu** (seed data).
    *   Sử dụng **Dependency Injection** và thực hiện so sánh sự khác biệt khi có và không sử dụng kỹ thuật này.
    *   Thiết kế API đúng chuẩn **mức 2**, trả về các mã lỗi đúng chuẩn.
    *   Có giải pháp để đạt được tính **Idempotency** và thực hiện **API versioning**.
    *   *Lưu ý:* Chưa cần tuân theo kiến trúc MVC.
*   **Bài tập 3: Phát triển từ bài tập 2**
    *   Xây dựng một ứng dụng web đơn giản với các chức năng phù hợp để sử dụng các endpoint đã được cung cấp bởi Web API ở bài tập trước.

#### **2. Nội dung nộp bài**

1.  **Báo cáo chi tiết:** Trình bày kết quả từng bài tập (đã làm được gì, kết quả ra sao) và liệt kê các kiến thức đã học được áp dụng.
2.  **Mã nguồn (Source code)**.
3.  **Video demo:** Một đoạn video ngắn dưới 1 phút minh họa chương trình.
4.  **Cơ sở dữ liệu:** SV tự tạo CSDL gồm 2-3 bảng với hơn 100 dòng dữ liệu mỗi bảng.

#### **3. Yêu cầu chi tiết nội dung nộp**

*   **Báo cáo (PDF hoặc Word):**
    *   Mô tả domain đã chọn và sơ đồ CSDL (ERD hoặc bảng mô tả).
    *   Danh sách các endpoint (kèm method, path, mô tả, và request/response schema).
    *   Trình bày cách implement từng yêu cầu kỹ thuật kèm ảnh chụp màn hình minh chứng.
    *   **Bài 1:** Cung cấp bảng kết quả từ công cụ **Locust** và trả lời các câu hỏi phân tích.
    *   **Bài 2:** So sánh việc dùng DI vs không dùng DI; giải thích về idempotency và versioning.
    *   **Bài 3:** Mô tả ứng dụng web đã cài đặt.
    *   Phần tự đánh giá mức độ hoàn thành các yêu cầu.
*   **Mã nguồn:**
    *   Phải chạy được dựa trên hướng dẫn trong file `README`.
    *   Có file `seed_data.py` hoặc script để tạo CSDL với hơn 100 dòng dữ liệu.
*   **Video demo (dưới 1 phút):**
    *   Thực hiện chạy server, mở giao diện `/docs`, gọi thử thành công 2–3 endpoint (có thể dùng Jupyter Notebook).
    *   Minh họa xử lý lỗi: gọi 1 request sai để thấy lỗi **422**; gọi 1 tài nguyên không tồn tại để thấy lỗi **404** theo chuẩn RFC 7807.
    *   Demo một vài tính năng tiêu biểu của ứng dụng web.
*   **Cơ sở dữ liệu (CSDL):** File SQLite hoặc script SQL tạo bảng và dữ liệu mẫu (2-3 bảng quan hệ, mỗi bảng 100+ dòng).

**Lưu ý chung:** Sinh viên được phép sử dụng AI để hỗ trợ, nhưng cần hiểu rõ những gì AI tạo ra để phục vụ quá trình học tập.