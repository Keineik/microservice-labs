package com.example.enrollment.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

/**
 * OpenFeign client for course-service, resolved by name via Eureka.
 */
@FeignClient(
        name = "course-service",
        path = "/api/courses",
        fallbackFactory = CourseClientFallbackFactory.class)
public interface CourseClient {

    @GetMapping("/{courseCode}")
    CourseDto getByCode(@PathVariable("courseCode") String courseCode);
}
