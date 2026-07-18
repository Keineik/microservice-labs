package com.example.enrollment.dto;

import com.example.enrollment.client.StudentDto;

/** Student details embedded in an aggregation response. */
public record StudentInfo(
        String studentCode,
        String fullName,
        String email,
        String major,
        Integer enrollmentYear) {

    public static StudentInfo from(StudentDto dto) {
        return new StudentInfo(
                dto.studentCode(),
                dto.fullName(),
                dto.email(),
                dto.major(),
                dto.enrollmentYear());
    }
}
