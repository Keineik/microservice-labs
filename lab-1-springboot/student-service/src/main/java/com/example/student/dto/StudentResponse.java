package com.example.student.dto;

import com.example.student.domain.Student;

/**
 * The public JSON shape of a student. Kept separate from the JPA entity so the
 * persistence model can evolve without silently changing the API contract that
 * other services depend on.
 */
public record StudentResponse(
        Long id,
        String studentCode,
        String fullName,
        String email,
        String major,
        Integer enrollmentYear) {

    public static StudentResponse from(Student student) {
        return new StudentResponse(
                student.getId(),
                student.getStudentCode(),
                student.getFullName(),
                student.getEmail(),
                student.getMajor(),
                student.getEnrollmentYear());
    }
}
