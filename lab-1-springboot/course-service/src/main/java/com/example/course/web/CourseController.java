package com.example.course.web;

import java.util.List;

import com.example.course.dto.CourseResponse;
import com.example.course.service.CourseService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/courses")
public class CourseController {

    private final CourseService service;

    public CourseController(CourseService service) {
        this.service = service;
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
}
