package com.example.enrollment.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/** Request body for registering a student in a course. */
public record CreateEnrollmentRequest(
        @NotBlank @Size(max = 20) String studentCode,
        @NotBlank @Size(max = 20) String courseCode) {
}
