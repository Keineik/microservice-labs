package com.example.course.service;

import java.util.List;

import com.example.course.domain.Course;
import com.example.course.dto.OfferingResponse;
import com.example.course.error.ResourceNotFoundException;
import com.example.course.repository.CourseOfferingRepository;
import com.example.course.repository.CourseRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class OfferingService {

    private final CourseOfferingRepository offerings;
    private final CourseRepository courses;

    public OfferingService(CourseOfferingRepository offerings, CourseRepository courses) {
        this.offerings = offerings;
        this.courses = courses;
    }

    /** One offering (with its course details) by business key. */
    @Transactional(readOnly = true)
    public OfferingResponse getByOfferingCode(String offeringCode) {
        var offering = offerings.findByOfferingCode(offeringCode)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "No offering with code '" + offeringCode + "'"));
        Course course = courses.findByCourseCode(offering.getCourseCode()).orElse(null);
        return OfferingResponse.of(offering, course);
    }

    /** All offerings of a course (which years/semesters/sections it was opened). */
    @Transactional(readOnly = true)
    public List<OfferingResponse> getByCourseCode(String courseCode) {
        Course course = courses.findByCourseCode(courseCode).orElse(null);
        return offerings.findByCourseCodeOrderByYearAscSemesterAscSectionAsc(courseCode).stream()
                .map(offering -> OfferingResponse.of(offering, course))
                .toList();
    }
}
