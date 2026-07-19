package com.example.course.dto;

import com.example.course.domain.Course;
import com.example.course.domain.CourseOffering;

/**
 * A course offering joined with its course details, so a single call gives a
 * consumer everything it needs (course title/credits/department + the
 * year/semester/section it was opened in). {@code credits} is boxed so it can be
 * null if the referenced course is somehow missing.
 */
public record OfferingResponse(
        String offeringCode,
        String courseCode,
        String courseTitle,
        Integer credits,
        String department,
        int year,
        int semester,
        String section,
        String instructor) {

    public static OfferingResponse of(CourseOffering offering, Course course) {
        return new OfferingResponse(
                offering.getOfferingCode(),
                offering.getCourseCode(),
                course != null ? course.getTitle() : null,
                course != null ? course.getCredits() : null,
                course != null ? course.getDepartment() : null,
                offering.getYear(),
                offering.getSemester(),
                offering.getSection(),
                offering.getInstructor());
    }
}
