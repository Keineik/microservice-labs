package com.example.enrollment.dto;

import java.util.List;

/**
 * The students attending one offering (with their results), returned by
 * {@code GET /api/enrollments/offering/{offeringCode}}. Student names are
 * resolved from student-service; {@code partial} is true if any of those
 * lookups was degraded.
 */
public record OfferingAttendeesResponse(
        String offeringCode,
        List<Attendee> attendees,
        boolean partial,
        List<String> warnings) {
}
