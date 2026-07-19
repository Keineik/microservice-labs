package com.example.enrollment.service;

import java.util.ArrayList;
import java.util.List;

import com.example.enrollment.client.OfferingClient;
import com.example.enrollment.client.OfferingDto;
import com.example.enrollment.client.StudentClient;
import com.example.enrollment.client.StudentDto;
import com.example.enrollment.domain.Enrollment;
import com.example.enrollment.domain.EnrollmentStatus;
import com.example.enrollment.dto.Attendee;
import com.example.enrollment.dto.CreateEnrollmentRequest;
import com.example.enrollment.dto.EnrolledCourse;
import com.example.enrollment.dto.OfferingAttendeesResponse;
import com.example.enrollment.dto.StudentEnrollmentsResponse;
import com.example.enrollment.dto.StudentInfo;
import com.example.enrollment.error.DuplicateResourceException;
import com.example.enrollment.error.ResourceNotFoundException;
import com.example.enrollment.repository.EnrollmentRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Owns enrollment records and composes the cross-service views. Enrollment rows
 * come from this service's own database; student and offering/course details are
 * fetched over Feign and combined here. If a downstream is unavailable the view
 * is still returned, flagged {@code partial}, rather than failing.
 */
@Service
public class EnrollmentService {

    private static final String COMPLETED = EnrollmentStatus.COMPLETED.name();
    private static final String REGISTERED = EnrollmentStatus.REGISTERED.name();

    private final EnrollmentRepository repository;
    private final StudentClient studentClient;
    private final OfferingClient offeringClient;

    public EnrollmentService(EnrollmentRepository repository,
                             StudentClient studentClient,
                             OfferingClient offeringClient) {
        this.repository = repository;
        this.studentClient = studentClient;
        this.offeringClient = offeringClient;
    }

    /** A student's transcript: enrollments enriched with offering/course details,
     *  plus credit totals and a credit-weighted cumulative GPA. */
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
        boolean anyOfferingDegraded = false;
        for (Enrollment row : rows) {
            OfferingDto offering = offeringClient.getByCode(row.getOfferingCode());
            boolean detailsAvailable = offering != null && offering.courseTitle() != null;
            if (!detailsAvailable) {
                anyOfferingDegraded = true;
            }
            enrolled.add(new EnrolledCourse(
                    row.getOfferingCode(),
                    offering != null ? offering.courseCode() : null,
                    detailsAvailable ? offering.courseTitle() : null,
                    detailsAvailable ? offering.credits() : null,
                    detailsAvailable ? offering.department() : null,
                    offering != null ? offering.year() : null,
                    offering != null ? offering.semester() : null,
                    offering != null ? offering.section() : null,
                    row.getStatus().name(),
                    row.getGrade(),
                    detailsAvailable));
        }
        if (anyOfferingDegraded) {
            warnings.add("course-service unavailable: some course details are incomplete");
        }

        int totalCourses = enrolled.size();
        int creditsEarned = sumCredits(enrolled, COMPLETED);
        int creditsInProgress = sumCredits(enrolled, REGISTERED);
        Double gpa = cumulativeGpa(enrolled);

        boolean partial = (student == null) || anyOfferingDegraded;
        return new StudentEnrollmentsResponse(studentCode, student, enrolled,
                totalCourses, creditsEarned, creditsInProgress, gpa, partial, warnings);
    }

    private static int sumCredits(List<EnrolledCourse> enrolled, String status) {
        return enrolled.stream()
                .filter(e -> status.equals(e.status()) && e.credits() != null)
                .mapToInt(e -> e.credits())
                .sum();
    }

    /** Credit-weighted average over COMPLETED, graded courses (0-10 scale). */
    private static Double cumulativeGpa(List<EnrolledCourse> enrolled) {
        int totalCredits = 0;
        double weighted = 0.0;
        for (EnrolledCourse e : enrolled) {
            if (COMPLETED.equals(e.status()) && e.grade() != null && e.credits() != null) {
                totalCredits += e.credits();
                weighted += e.grade() * e.credits();
            }
        }
        if (totalCredits == 0) {
            return null;
        }
        return Math.round(weighted / totalCredits * 100.0) / 100.0;
    }

    /** The students attending an offering, with names resolved from student-service. */
    @Transactional(readOnly = true)
    public OfferingAttendeesResponse getOfferingAttendees(String offeringCode) {
        List<String> warnings = new ArrayList<>();
        List<Enrollment> rows = repository.findByOfferingCode(offeringCode);

        List<Attendee> attendees = new ArrayList<>();
        boolean anyStudentDegraded = false;
        for (Enrollment row : rows) {
            StudentDto studentDto = resolveStudent(row.getStudentCode());
            boolean available = studentDto != null;
            if (!available) {
                anyStudentDegraded = true;
            }
            attendees.add(new Attendee(
                    row.getStudentCode(),
                    available ? studentDto.fullName() : null,
                    available ? studentDto.major() : null,
                    row.getStatus().name(),
                    row.getGrade(),
                    available));
        }
        if (anyStudentDegraded) {
            warnings.add("student-service unavailable: some student names are missing");
        }
        return new OfferingAttendeesResponse(offeringCode, attendees, anyStudentDegraded, warnings);
    }

    private StudentDto resolveStudent(String studentCode) {
        try {
            return studentClient.getByCode(studentCode);
        } catch (ResourceNotFoundException ex) {
            // Here the studentCode came from a real enrollment; treat a missing
            // student as unavailable rather than failing the whole listing.
            return null;
        }
    }

    @Transactional(readOnly = true)
    public List<Enrollment> listAll() {
        return repository.findAll();
    }

    @Transactional
    public Enrollment register(CreateEnrollmentRequest request) {
        boolean alreadyActive = repository.existsByStudentCodeAndOfferingCodeAndStatus(
                request.studentCode(), request.offeringCode(), EnrollmentStatus.REGISTERED);
        if (alreadyActive) {
            throw new DuplicateResourceException("Student '" + request.studentCode()
                    + "' is already registered in offering '" + request.offeringCode() + "'");
        }
        return repository.save(new Enrollment(
                request.studentCode(), request.offeringCode(), EnrollmentStatus.REGISTERED, null));
    }
}
