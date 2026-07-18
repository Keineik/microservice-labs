package com.example.enrollment.service;

import java.util.ArrayList;
import java.util.List;

import com.example.enrollment.client.CourseClient;
import com.example.enrollment.client.CourseDto;
import com.example.enrollment.client.StudentClient;
import com.example.enrollment.client.StudentDto;
import com.example.enrollment.domain.Enrollment;
import com.example.enrollment.domain.EnrollmentStatus;
import com.example.enrollment.dto.CreateEnrollmentRequest;
import com.example.enrollment.dto.EnrolledCourse;
import com.example.enrollment.dto.StudentEnrollmentsResponse;
import com.example.enrollment.dto.StudentInfo;
import com.example.enrollment.error.DuplicateResourceException;
import com.example.enrollment.repository.EnrollmentRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Owns enrollment records and composes the cross-service aggregation. This is
 * where the two Feign calls (student-service, course-service) are combined with
 * this service's own data into one response.
 */
@Service
public class EnrollmentService {

    private final EnrollmentRepository repository;
    private final StudentClient studentClient;
    private final CourseClient courseClient;

    public EnrollmentService(EnrollmentRepository repository,
                             StudentClient studentClient,
                             CourseClient courseClient) {
        this.repository = repository;
        this.studentClient = studentClient;
        this.courseClient = courseClient;
    }

    /**
     * Build a student's full enrollment view. Enrollment rows come from this
     * service's own database; student and course details are fetched over Feign.
     * If a downstream is unavailable the response is still returned, flagged as
     * {@code partial} with explanatory warnings, rather than failing.
     */
    @Transactional(readOnly = true)
    public StudentEnrollmentsResponse getStudentEnrollments(String studentCode) {
        List<String> warnings = new ArrayList<>();

        // A genuine 404 from student-service propagates (see the fallback factory);
        // a real outage yields null and we continue in degraded mode.
        StudentDto studentDto = studentClient.getByCode(studentCode);
        StudentInfo student = null;
        if (studentDto != null) {
            student = StudentInfo.from(studentDto);
        } else {
            warnings.add("student-service unavailable: student details omitted");
        }

        List<Enrollment> rows = repository.findByStudentCode(studentCode);

        List<EnrolledCourse> enrolled = new ArrayList<>();
        boolean anyCourseDegraded = false;
        for (Enrollment row : rows) {
            CourseDto course = courseClient.getByCode(row.getCourseCode());
            boolean detailsAvailable = course != null && course.title() != null;
            if (!detailsAvailable) {
                anyCourseDegraded = true;
            }
            enrolled.add(new EnrolledCourse(
                    row.getCourseCode(),
                    detailsAvailable ? course.title() : null,
                    detailsAvailable ? course.credits() : null,
                    detailsAvailable ? course.department() : null,
                    row.getStatus().name(),
                    row.getGrade(),
                    detailsAvailable));
        }
        if (anyCourseDegraded) {
            warnings.add("course-service unavailable: some course details are incomplete");
        }

        boolean partial = (student == null) || anyCourseDegraded;
        return new StudentEnrollmentsResponse(studentCode, student, enrolled, partial, warnings);
    }

    @Transactional(readOnly = true)
    public List<Enrollment> listAll() {
        return repository.findAll();
    }

    @Transactional
    public Enrollment register(CreateEnrollmentRequest request) {
        boolean alreadyActive = repository.existsByStudentCodeAndCourseCodeAndStatus(
                request.studentCode(), request.courseCode(), EnrollmentStatus.REGISTERED);
        if (alreadyActive) {
            throw new DuplicateResourceException("Student '" + request.studentCode()
                    + "' is already registered in course '" + request.courseCode() + "'");
        }
        return repository.save(new Enrollment(
                request.studentCode(), request.courseCode(), EnrollmentStatus.REGISTERED, null));
    }
}
