package com.example.enrollment.config;

import java.util.List;

import com.example.enrollment.domain.Enrollment;
import com.example.enrollment.domain.EnrollmentStatus;
import com.example.enrollment.repository.EnrollmentRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Seeds enrollment links on startup. Every studentCode/courseCode here matches a
 * record seeded in student-service / course-service, so the aggregation resolves
 * real details.
 */
@Configuration
public class DataSeeder {

    @Bean
    CommandLineRunner seedEnrollments(EnrollmentRepository repository) {
        return args -> {
            if (repository.count() > 0) {
                return;
            }
            repository.saveAll(List.of(
                    // SV001 - a mix of completed (with grades) and active courses.
                    new Enrollment("SV001", "CS101", EnrollmentStatus.COMPLETED, 8.5),
                    new Enrollment("SV001", "CS102", EnrollmentStatus.COMPLETED, 7.0),
                    new Enrollment("SV001", "CS202", EnrollmentStatus.REGISTERED, null),
                    new Enrollment("SV001", "CS301", EnrollmentStatus.REGISTERED, null),
                    // SV002
                    new Enrollment("SV002", "CS101", EnrollmentStatus.COMPLETED, 9.0),
                    new Enrollment("SV002", "MATH101", EnrollmentStatus.COMPLETED, 8.0),
                    new Enrollment("SV002", "CS202", EnrollmentStatus.REGISTERED, null),
                    // SV003
                    new Enrollment("SV003", "IS101", EnrollmentStatus.COMPLETED, 7.5),
                    new Enrollment("SV003", "CS101", EnrollmentStatus.REGISTERED, null),
                    // SV004
                    new Enrollment("SV004", "CS102", EnrollmentStatus.COMPLETED, 6.5),
                    new Enrollment("SV004", "SE201", EnrollmentStatus.REGISTERED, null),
                    // SV005 - strong record.
                    new Enrollment("SV005", "CS101", EnrollmentStatus.COMPLETED, 9.5),
                    new Enrollment("SV005", "CS102", EnrollmentStatus.COMPLETED, 9.0),
                    new Enrollment("SV005", "CS201", EnrollmentStatus.COMPLETED, 8.5),
                    new Enrollment("SV005", "CS301", EnrollmentStatus.REGISTERED, null),
                    // SV006
                    new Enrollment("SV006", "DS201", EnrollmentStatus.REGISTERED, null),
                    new Enrollment("SV006", "MATH101", EnrollmentStatus.REGISTERED, null),
                    // SV007
                    new Enrollment("SV007", "SE201", EnrollmentStatus.COMPLETED, 8.0),
                    new Enrollment("SV007", "CS202", EnrollmentStatus.REGISTERED, null),
                    // SV008
                    new Enrollment("SV008", "IS101", EnrollmentStatus.REGISTERED, null)));
        };
    }
}
