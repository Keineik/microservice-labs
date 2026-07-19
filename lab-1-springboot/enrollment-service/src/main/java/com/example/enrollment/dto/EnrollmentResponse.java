package com.example.enrollment.dto;

import java.time.Instant;

import com.example.enrollment.domain.Enrollment;

/** Flat JSON shape of a single enrollment record (no cross-service enrichment). */
public record EnrollmentResponse(
        Long id,
        String studentCode,
        String offeringCode,
        String status,
        Double grade,
        Instant registeredAt) {

    public static EnrollmentResponse from(Enrollment enrollment) {
        return new EnrollmentResponse(
                enrollment.getId(),
                enrollment.getStudentCode(),
                enrollment.getOfferingCode(),
                enrollment.getStatus().name(),
                enrollment.getGrade(),
                enrollment.getRegisteredAt());
    }
}
