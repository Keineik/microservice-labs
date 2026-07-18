package com.example.enrollment.client;

/**
 * This service's view of a course, as returned by course-service. {@code credits}
 * is a boxed Integer so a fallback placeholder can leave it null when
 * course-service is unavailable.
 */
public record CourseDto(
        String courseCode,
        String title,
        Integer credits,
        String department) {
}
