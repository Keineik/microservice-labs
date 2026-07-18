package com.example.enrollment.client;

/**
 * This service's view of a student, as returned by student-service. It is a
 * deliberate subset of the producer's contract - a consumer-driven view that
 * takes only the fields this service needs. Unknown JSON fields are ignored.
 */
public record StudentDto(
        String studentCode,
        String fullName,
        String email,
        String major,
        Integer enrollmentYear) {
}
