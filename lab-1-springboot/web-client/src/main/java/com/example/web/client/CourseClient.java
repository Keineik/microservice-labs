package com.example.web.client;

import java.util.List;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

/** Feign client for course-service, resolved by name via Eureka. */
@FeignClient(name = "course-service", path = "/api/courses")
public interface CourseClient {

    @GetMapping
    List<CourseView> list();

    @GetMapping("/{courseCode}")
    CourseView getByCode(@PathVariable("courseCode") String courseCode);

    @GetMapping("/{courseCode}/offerings")
    List<OfferingView> offerings(@PathVariable("courseCode") String courseCode);
}
