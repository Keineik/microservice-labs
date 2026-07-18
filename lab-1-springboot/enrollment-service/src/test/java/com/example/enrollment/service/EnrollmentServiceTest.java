package com.example.enrollment.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import java.util.List;

import com.example.enrollment.client.CourseClient;
import com.example.enrollment.client.CourseDto;
import com.example.enrollment.client.StudentClient;
import com.example.enrollment.client.StudentDto;
import com.example.enrollment.domain.Enrollment;
import com.example.enrollment.domain.EnrollmentStatus;
import com.example.enrollment.dto.StudentEnrollmentsResponse;
import com.example.enrollment.repository.EnrollmentRepository;
import org.junit.jupiter.api.Test;

/**
 * Unit tests for the aggregation logic, with the Feign clients mocked. These
 * exercise the happy path and both degraded paths (each downstream down) without
 * needing a running Eureka or the other services.
 */
class EnrollmentServiceTest {

    private final EnrollmentRepository repository = mock(EnrollmentRepository.class);
    private final StudentClient studentClient = mock(StudentClient.class);
    private final CourseClient courseClient = mock(CourseClient.class);
    private final EnrollmentService service =
            new EnrollmentService(repository, studentClient, courseClient);

    @Test
    void aggregatesStudentAndCourseDetails() {
        when(studentClient.getByCode("SV001")).thenReturn(
                new StudentDto("SV001", "Nguyen Van An", "an.nguyen@example.edu", "Computer Science", 2022));
        when(repository.findByStudentCode("SV001")).thenReturn(
                List.of(new Enrollment("SV001", "CS101", EnrollmentStatus.COMPLETED, 8.5)));
        when(courseClient.getByCode("CS101")).thenReturn(
                new CourseDto("CS101", "Introduction to Programming", 3, "Computer Science"));

        StudentEnrollmentsResponse response = service.getStudentEnrollments("SV001");

        assertThat(response.partial()).isFalse();
        assertThat(response.student()).isNotNull();
        assertThat(response.student().fullName()).isEqualTo("Nguyen Van An");
        assertThat(response.enrollments()).hasSize(1);
        assertThat(response.enrollments().get(0).detailsAvailable()).isTrue();
        assertThat(response.enrollments().get(0).title()).isEqualTo("Introduction to Programming");
        assertThat(response.enrollments().get(0).grade()).isEqualTo(8.5);
    }

    @Test
    void marksPartialWhenStudentServiceIsDown() {
        // Fallback returns null when student-service is unreachable.
        when(studentClient.getByCode("SV001")).thenReturn(null);
        when(repository.findByStudentCode("SV001")).thenReturn(
                List.of(new Enrollment("SV001", "CS101", EnrollmentStatus.REGISTERED, null)));
        when(courseClient.getByCode("CS101")).thenReturn(
                new CourseDto("CS101", "Introduction to Programming", 3, "Computer Science"));

        StudentEnrollmentsResponse response = service.getStudentEnrollments("SV001");

        assertThat(response.partial()).isTrue();
        assertThat(response.student()).isNull();
        assertThat(response.warnings()).isNotEmpty();
        // Enrollment rows still come from this service's own database.
        assertThat(response.enrollments()).hasSize(1);
    }

    @Test
    void marksPartialWhenCourseServiceIsDown() {
        when(studentClient.getByCode("SV001")).thenReturn(
                new StudentDto("SV001", "Nguyen Van An", "an.nguyen@example.edu", "Computer Science", 2022));
        when(repository.findByStudentCode("SV001")).thenReturn(
                List.of(new Enrollment("SV001", "CS101", EnrollmentStatus.REGISTERED, null)));
        // Fallback placeholder carries only the code (title/credits null).
        when(courseClient.getByCode("CS101")).thenReturn(new CourseDto("CS101", null, null, null));

        StudentEnrollmentsResponse response = service.getStudentEnrollments("SV001");

        assertThat(response.partial()).isTrue();
        assertThat(response.enrollments().get(0).detailsAvailable()).isFalse();
        assertThat(response.enrollments().get(0).courseCode()).isEqualTo("CS101");
    }
}
