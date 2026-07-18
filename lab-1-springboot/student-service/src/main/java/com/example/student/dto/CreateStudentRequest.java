package com.example.student.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * Request body for creating a student. Bean Validation constraints are enforced
 * by {@code @Valid} in the controller before the service is called.
 */
public record CreateStudentRequest(
        @NotBlank @Size(max = 20) String studentCode,
        @NotBlank @Size(max = 200) String fullName,
        @NotBlank @Email @Size(max = 255) String email,
        @Size(max = 100) String major,
        Integer enrollmentYear) {
}
