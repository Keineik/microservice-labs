package com.example.enrollment.config;

import java.util.List;

import com.example.enrollment.domain.Enrollment;
import com.example.enrollment.domain.EnrollmentStatus;
import com.example.enrollment.repository.EnrollmentRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Seeds enrollment links on startup. Every offeringCode here matches an offering
 * seeded in course-service, and every studentCode matches a student seeded in
 * student-service, so the aggregation resolves real details.
 *
 * <p>COMPLETED rows are in past terms (2024) and carry grades; REGISTERED rows
 * are in the current term (2025 HK1).
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
                    // SV001 - two completed (graded) + two current.
                    new Enrollment("SV001", "CS101-2024-1-01", EnrollmentStatus.COMPLETED, 8.5),
                    new Enrollment("SV001", "CS102-2024-2-01", EnrollmentStatus.COMPLETED, 7.0),
                    new Enrollment("SV001", "CS202-2025-1-01", EnrollmentStatus.REGISTERED, null),
                    new Enrollment("SV001", "CS301-2025-1-01", EnrollmentStatus.REGISTERED, null),
                    // SV002
                    new Enrollment("SV002", "CS101-2024-1-01", EnrollmentStatus.COMPLETED, 9.0),
                    new Enrollment("SV002", "MATH101-2024-1-01", EnrollmentStatus.COMPLETED, 8.0),
                    new Enrollment("SV002", "CS202-2025-1-01", EnrollmentStatus.REGISTERED, null),
                    // SV003
                    new Enrollment("SV003", "IS101-2024-1-01", EnrollmentStatus.COMPLETED, 7.5),
                    new Enrollment("SV003", "CS101-2025-1-01", EnrollmentStatus.REGISTERED, null),
                    // SV004
                    new Enrollment("SV004", "CS102-2024-2-01", EnrollmentStatus.COMPLETED, 6.5),
                    new Enrollment("SV004", "SE201-2025-1-01", EnrollmentStatus.REGISTERED, null),
                    // SV005 - strong record across two past terms.
                    new Enrollment("SV005", "CS101-2024-1-01", EnrollmentStatus.COMPLETED, 9.5),
                    new Enrollment("SV005", "CS102-2024-2-01", EnrollmentStatus.COMPLETED, 9.0),
                    new Enrollment("SV005", "CS201-2024-2-01", EnrollmentStatus.COMPLETED, 8.5),
                    new Enrollment("SV005", "CS301-2025-1-01", EnrollmentStatus.REGISTERED, null),
                    // SV006 - only current registrations (no GPA yet).
                    new Enrollment("SV006", "DS201-2025-1-01", EnrollmentStatus.REGISTERED, null),
                    new Enrollment("SV006", "MATH201-2025-1-01", EnrollmentStatus.REGISTERED, null),
                    // SV007
                    new Enrollment("SV007", "SE201-2024-2-01", EnrollmentStatus.COMPLETED, 8.0),
                    new Enrollment("SV007", "CS202-2025-1-01", EnrollmentStatus.REGISTERED, null),
                    // SV008 - registered in the second section of CS101 (2025 HK1).
                    new Enrollment("SV008", "CS101-2025-1-02", EnrollmentStatus.REGISTERED, null)));
        };
    }
}
