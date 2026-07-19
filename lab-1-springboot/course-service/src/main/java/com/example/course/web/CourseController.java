package com.example.course.web;

import java.util.List;

import com.example.course.dto.CourseResponse;
import com.example.course.dto.OfferingResponse;
import com.example.course.service.CourseService;
import com.example.course.service.OfferingService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/courses")
public class CourseController {

    private final CourseService service;
    private final OfferingService offeringService;

    public CourseController(CourseService service, OfferingService offeringService) {
        this.service = service;
        this.offeringService = offeringService;
    }

    /** List all courses. */
    @GetMapping
    public List<CourseResponse> list() {
        return service.listAll();
    }

    /** Get one course by its business key (courseCode). */
    @GetMapping("/{courseCode}")
    public CourseResponse getByCode(@PathVariable String courseCode) {
        return service.getByCode(courseCode);
    }

    /** List the offerings of a course (which years/semesters/sections it ran in). */
    @GetMapping("/{courseCode}/offerings")
    public List<OfferingResponse> offerings(@PathVariable String courseCode) {
        return offeringService.getByCourseCode(courseCode);
    }
}
