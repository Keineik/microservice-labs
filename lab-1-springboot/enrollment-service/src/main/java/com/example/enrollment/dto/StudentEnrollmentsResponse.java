package com.example.enrollment.dto;

import java.util.List;

/**
 * The aggregated view returned by {@code GET /api/enrollments/student/{code}}:
 * the student's details plus every course they are enrolled in.
 *
 * @param studentCode the student, always known (it is the request key)
 * @param student     student details, or null if student-service was unavailable
 * @param enrollments the student's courses (from this service's own DB), each
 *                    enriched with course details when course-service is reachable
 * @param partial     true if any downstream data is degraded/missing
 * @param warnings    human-readable notes about what was degraded
 */
public record StudentEnrollmentsResponse(
        String studentCode,
        StudentInfo student,
        List<EnrolledCourse> enrollments,
        boolean partial,
        List<String> warnings) {
}
