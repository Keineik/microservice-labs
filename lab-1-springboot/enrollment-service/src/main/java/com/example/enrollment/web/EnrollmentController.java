package com.example.enrollment.web;

import java.net.URI;
import java.util.List;

import com.example.enrollment.domain.Enrollment;
import com.example.enrollment.dto.CreateEnrollmentRequest;
import com.example.enrollment.dto.EnrollmentResponse;
import com.example.enrollment.dto.OfferingAttendeesResponse;
import com.example.enrollment.dto.StudentEnrollmentsResponse;
import com.example.enrollment.service.EnrollmentService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.util.UriComponentsBuilder;

@RestController
@RequestMapping("/api/enrollments")
public class EnrollmentController {

    private final EnrollmentService service;

    public EnrollmentController(EnrollmentService service) {
        this.service = service;
    }

    /** A student's transcript, enriched via OpenFeign with offering/course
     *  details plus credit totals and cumulative GPA. */
    @GetMapping("/student/{studentCode}")
    public StudentEnrollmentsResponse getStudentEnrollments(@PathVariable String studentCode) {
        return service.getStudentEnrollments(studentCode);
    }

    /** The students attending one offering, with their results (names resolved
     *  via OpenFeign from student-service). */
    @GetMapping("/offering/{offeringCode}")
    public OfferingAttendeesResponse getOfferingAttendees(@PathVariable String offeringCode) {
        return service.getOfferingAttendees(offeringCode);
    }

    /** Raw enrollment records (no enrichment) - handy for debugging. */
    @GetMapping
    public List<EnrollmentResponse> list() {
        return service.listAll().stream().map(EnrollmentResponse::from).toList();
    }

    /** Register a student in a course offering. */
    @PostMapping
    public ResponseEntity<EnrollmentResponse> register(
            @Valid @RequestBody CreateEnrollmentRequest request,
            UriComponentsBuilder uriBuilder) {
        Enrollment created = service.register(request);
        URI location = uriBuilder.path("/api/enrollments/{id}")
                .buildAndExpand(created.getId())
                .toUri();
        return ResponseEntity.created(location).body(EnrollmentResponse.from(created));
    }
}
