package com.example.enrollment.dto;

/**
 * One student attending an offering, with their result. {@code fullName}/major
 * come from student-service; {@code studentAvailable} is false if that lookup
 * was degraded (then only the studentCode is known).
 */
public record Attendee(
        String studentCode,
        String fullName,
        String major,
        String status,
        Double grade,
        boolean studentAvailable) {
}
