package com.example.enrollment.dto;

import java.util.List;

/**
 * The aggregated transcript returned by
 * {@code GET /api/enrollments/student/{code}}: the student's details, every
 * course they are enrolled in, and derived academic figures.
 *
 * @param student          student details, or null if student-service was unavailable
 * @param totalCourses     number of enrollment records
 * @param creditsEarned    sum of credits of COMPLETED courses
 * @param creditsInProgress sum of credits of REGISTERED courses
 * @param cumulativeGpa    credit-weighted average over COMPLETED graded courses
 *                         (0-10 scale), or null if none yet
 * @param partial          true if any downstream detail is degraded/missing
 */
public record StudentEnrollmentsResponse(
        String studentCode,
        StudentInfo student,
        List<EnrolledCourse> enrollments,
        int totalCourses,
        int creditsEarned,
        int creditsInProgress,
        Double cumulativeGpa,
        boolean partial,
        List<String> warnings) {
}
