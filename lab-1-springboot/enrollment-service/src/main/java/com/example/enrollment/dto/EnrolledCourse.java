package com.example.enrollment.dto;

/**
 * One row in a student's transcript: the enrollment facts owned by this service
 * (status, grade) joined with the offering + course details fetched from
 * course-service. {@code detailsAvailable} is false when course-service could
 * not be reached (only the codes are known).
 */
public record EnrolledCourse(
        String offeringCode,
        String courseCode,
        String courseTitle,
        Integer credits,
        String department,
        Integer year,
        Integer semester,
        String section,
        String status,
        Double grade,
        boolean detailsAvailable) {
}
