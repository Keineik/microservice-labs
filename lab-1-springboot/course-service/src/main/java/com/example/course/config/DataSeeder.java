package com.example.course.config;

import java.util.List;

import com.example.course.domain.Course;
import com.example.course.domain.CourseOffering;
import com.example.course.repository.CourseOfferingRepository;
import com.example.course.repository.CourseRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Seeds the course catalog and its offerings on startup.
 *
 * <p>Three terms are represented: 2024 HK1 and 2024 HK2 (past) and 2025 HK1
 * (current). CS101 is opened in two sections in the current term to exercise the
 * multi-section case. Every offeringCode here is referenced by enrollment-service's
 * seed data, so cross-service lookups resolve.
 */
@Configuration
public class DataSeeder {

    @Bean
    CommandLineRunner seedCatalog(CourseRepository courses, CourseOfferingRepository offerings) {
        return args -> {
            if (courses.count() == 0) {
                courses.saveAll(List.of(
                        new Course("CS101", "Introduction to Programming", 3, "Computer Science",
                                "Nhập môn lập trình: biến, kiểu dữ liệu, cấu trúc điều khiển, hàm."),
                        new Course("CS102", "Data Structures and Algorithms", 4, "Computer Science",
                                "Cấu trúc dữ liệu và giải thuật cơ bản: danh sách, cây, đồ thị, sắp xếp, tìm kiếm."),
                        new Course("CS201", "Operating Systems", 3, "Computer Science",
                                "Tiến trình, luồng, quản lý bộ nhớ, hệ thống tập tin."),
                        new Course("CS202", "Database Systems", 3, "Computer Science",
                                "Mô hình quan hệ, SQL, thiết kế và chuẩn hóa cơ sở dữ liệu."),
                        new Course("CS301", "Distributed Systems", 3, "Computer Science",
                                "Hệ phân tán: giao tiếp giữa các tiến trình, nhất quán, chịu lỗi."),
                        new Course("SE201", "Software Engineering", 3, "Software Engineering",
                                "Quy trình phát triển phần mềm, phân tích yêu cầu, kiểm thử."),
                        new Course("IS101", "Information Systems Fundamentals", 3, "Information Systems",
                                "Nền tảng hệ thống thông tin trong tổ chức và doanh nghiệp."),
                        new Course("MATH101", "Calculus I", 4, "Mathematics",
                                "Giới hạn, đạo hàm, tích phân của hàm một biến."),
                        new Course("MATH201", "Linear Algebra", 3, "Mathematics",
                                "Ma trận, định thức, không gian vector, hệ phương trình tuyến tính."),
                        new Course("DS201", "Introduction to Data Science", 3, "Data Science",
                                "Nhập môn khoa học dữ liệu: xử lý, trực quan hóa và phân tích dữ liệu.")));
            }

            if (offerings.count() == 0) {
                offerings.saveAll(List.of(
                        // 2024 HK1 (past)
                        new CourseOffering("CS101", 2024, 1, "01", "TS. Le Minh Hoang"),
                        new CourseOffering("IS101", 2024, 1, "01", "ThS. Hoang Thi Lan"),
                        new CourseOffering("MATH101", 2024, 1, "01", "TS. Do Van Khai"),
                        // 2024 HK2 (past)
                        new CourseOffering("CS102", 2024, 2, "01", "TS. Nguyen Duc Anh"),
                        new CourseOffering("CS201", 2024, 2, "01", "TS. Pham Quoc Bao"),
                        new CourseOffering("SE201", 2024, 2, "01", "TS. Bui Thanh Son"),
                        // 2025 HK1 (current)
                        new CourseOffering("CS101", 2025, 1, "01", "TS. Le Minh Hoang"),
                        new CourseOffering("CS101", 2025, 1, "02", "ThS. Tran Thu Ha"),
                        new CourseOffering("CS202", 2025, 1, "01", "TS. Vo Thi Ngoc"),
                        new CourseOffering("CS301", 2025, 1, "01", "PGS. TS. Dang Van Minh"),
                        new CourseOffering("SE201", 2025, 1, "01", "TS. Bui Thanh Son"),
                        new CourseOffering("MATH201", 2025, 1, "01", "TS. Do Van Khai"),
                        new CourseOffering("DS201", 2025, 1, "01", "TS. Vo Thi Ngoc")));
            }
        };
    }
}
