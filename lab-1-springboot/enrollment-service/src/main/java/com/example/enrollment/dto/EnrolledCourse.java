package com.example.enrollment.dto;

/**
 * One row in a student's enrollment list: the enrollment facts owned by this
 * service (status, grade) joined with the course details fetched from
 * course-service. {@code detailsAvailable} is false when course-service could
 * not be reached and only the {@code courseCode} is known.
 */
public record EnrolledCourse(
        String courseCode,
        String title,
        Integer credits,
        String department,
        String status,
        Double grade,
        boolean detailsAvailable) {
}
