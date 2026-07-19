package com.example.enrollment.client;

/**
 * This service's view of a course offering, as returned by course-service
 * ({@code GET /api/offerings/{code}}). It joins the offering (year/semester/
 * section/instructor) with its course (title/credits/department) so one call
 * gives everything the transcript needs. Boxed numbers so a fallback placeholder
 * can leave them null.
 */
public record OfferingDto(
        String offeringCode,
        String courseCode,
        String courseTitle,
        Integer credits,
        String department,
        Integer year,
        Integer semester,
        String section,
        String instructor) {
}
