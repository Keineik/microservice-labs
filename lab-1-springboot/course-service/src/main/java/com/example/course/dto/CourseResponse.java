package com.example.course.dto;

import com.example.course.domain.Course;

/** Public JSON shape of a course. */
public record CourseResponse(
        Long id,
        String courseCode,
        String title,
        int credits,
        String department,
        String description) {

    public static CourseResponse from(Course course) {
        return new CourseResponse(
                course.getId(),
                course.getCourseCode(),
                course.getTitle(),
                course.getCredits(),
                course.getDepartment(),
                course.getDescription());
    }
}
