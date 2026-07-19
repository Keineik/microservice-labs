package com.example.enrollment.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import java.util.List;

import com.example.enrollment.client.OfferingClient;
import com.example.enrollment.client.OfferingDto;
import com.example.enrollment.client.StudentClient;
import com.example.enrollment.client.StudentDto;
import com.example.enrollment.domain.Enrollment;
import com.example.enrollment.domain.EnrollmentStatus;
import com.example.enrollment.dto.OfferingAttendeesResponse;
import com.example.enrollment.dto.StudentEnrollmentsResponse;
import com.example.enrollment.repository.EnrollmentRepository;
import org.junit.jupiter.api.Test;

/**
 * Unit tests for the aggregation logic, with the Feign clients mocked. Exercises
 * the happy path (offering + course details, GPA/credits), both degraded paths,
 * and the offering-attendees listing - all without a running Eureka or the other
 * services.
 */
class EnrollmentServiceTest {

    private final EnrollmentRepository repository = mock(EnrollmentRepository.class);
    private final StudentClient studentClient = mock(StudentClient.class);
    private final OfferingClient offeringClient = mock(OfferingClient.class);
    private final EnrollmentService service =
            new EnrollmentService(repository, studentClient, offeringClient);

    private static StudentDto student(String code) {
        return new StudentDto(code, "Nguyen Van An", code.toLowerCase() + "@example.edu",
                "Computer Science", 2022);
    }

    private static OfferingDto offering(String offeringCode, String courseCode, String title,
                                        int credits, int year, int semester) {
        return new OfferingDto(offeringCode, courseCode, title, credits, "Computer Science",
                year, semester, "01", "TS. Le Minh Hoang");
    }

    @Test
    void aggregatesTranscriptWithCreditsAndGpa() {
        when(studentClient.getByCode("SV001")).thenReturn(student("SV001"));
        when(repository.findByStudentCode("SV001")).thenReturn(List.of(
                new Enrollment("SV001", "CS101-2024-1-01", EnrollmentStatus.COMPLETED, 8.0),
                new Enrollment("SV001", "CS102-2024-2-01", EnrollmentStatus.COMPLETED, 9.0),
                new Enrollment("SV001", "CS202-2025-1-01", EnrollmentStatus.REGISTERED, null)));
        when(offeringClient.getByCode("CS101-2024-1-01"))
                .thenReturn(offering("CS101-2024-1-01", "CS101", "Introduction to Programming", 3, 2024, 1));
        when(offeringClient.getByCode("CS102-2024-2-01"))
                .thenReturn(offering("CS102-2024-2-01", "CS102", "Data Structures", 4, 2024, 2));
        when(offeringClient.getByCode("CS202-2025-1-01"))
                .thenReturn(offering("CS202-2025-1-01", "CS202", "Database Systems", 3, 2025, 1));

        StudentEnrollmentsResponse response = service.getStudentEnrollments("SV001");

        assertThat(response.partial()).isFalse();
        assertThat(response.student().fullName()).isEqualTo("Nguyen Van An");
        assertThat(response.totalCourses()).isEqualTo(3);
        assertThat(response.creditsEarned()).isEqualTo(7);       // 3 + 4 completed
        assertThat(response.creditsInProgress()).isEqualTo(3);   // CS202 registered
        // Credit-weighted: (8.0*3 + 9.0*4) / 7 = 60/7 = 8.57
        assertThat(response.cumulativeGpa()).isEqualTo(8.57);
        assertThat(response.enrollments()).hasSize(3);
        assertThat(response.enrollments().get(0).year()).isEqualTo(2024);
    }

    @Test
    void marksPartialWhenStudentServiceIsDown() {
        when(studentClient.getByCode("SV001")).thenReturn(null); // fallback (degraded)
        when(repository.findByStudentCode("SV001")).thenReturn(List.of(
                new Enrollment("SV001", "CS101-2024-1-01", EnrollmentStatus.COMPLETED, 8.0)));
        when(offeringClient.getByCode("CS101-2024-1-01"))
                .thenReturn(offering("CS101-2024-1-01", "CS101", "Introduction to Programming", 3, 2024, 1));

        StudentEnrollmentsResponse response = service.getStudentEnrollments("SV001");

        assertThat(response.partial()).isTrue();
        assertThat(response.student()).isNull();
        assertThat(response.warnings()).isNotEmpty();
        assertThat(response.enrollments()).hasSize(1); // enrollments still from own DB
    }

    @Test
    void marksPartialWhenOfferingDetailsUnavailable() {
        when(studentClient.getByCode("SV001")).thenReturn(student("SV001"));
        when(repository.findByStudentCode("SV001")).thenReturn(List.of(
                new Enrollment("SV001", "CS101-2024-1-01", EnrollmentStatus.COMPLETED, 8.0)));
        // Fallback placeholder: title null (course-service down), credits null.
        when(offeringClient.getByCode("CS101-2024-1-01"))
                .thenReturn(new OfferingDto("CS101-2024-1-01", "CS101", null, null, null, 2024, 1, "01", null));

        StudentEnrollmentsResponse response = service.getStudentEnrollments("SV001");

        assertThat(response.partial()).isTrue();
        assertThat(response.enrollments().get(0).detailsAvailable()).isFalse();
        assertThat(response.enrollments().get(0).courseCode()).isEqualTo("CS101");
        // No credits resolved, so GPA cannot be computed.
        assertThat(response.cumulativeGpa()).isNull();
        assertThat(response.creditsEarned()).isZero();
    }

    @Test
    void listsOfferingAttendeesWithNames() {
        when(repository.findByOfferingCode("CS101-2024-1-01")).thenReturn(List.of(
                new Enrollment("SV001", "CS101-2024-1-01", EnrollmentStatus.COMPLETED, 8.5),
                new Enrollment("SV002", "CS101-2024-1-01", EnrollmentStatus.COMPLETED, 9.0)));
        when(studentClient.getByCode(anyString())).thenReturn(student("SV001"));

        OfferingAttendeesResponse response = service.getOfferingAttendees("CS101-2024-1-01");

        assertThat(response.partial()).isFalse();
        assertThat(response.attendees()).hasSize(2);
        assertThat(response.attendees().get(0).studentAvailable()).isTrue();
        assertThat(response.attendees().get(0).grade()).isEqualTo(8.5);
    }
}
