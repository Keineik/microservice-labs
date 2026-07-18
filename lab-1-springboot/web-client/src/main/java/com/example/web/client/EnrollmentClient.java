package com.example.web.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

/** Feign client for enrollment-service, resolved by name via Eureka. */
@FeignClient(name = "enrollment-service", path = "/api/enrollments")
public interface EnrollmentClient {

    @GetMapping("/student/{studentCode}")
    StudentEnrollmentsView getStudentEnrollments(@PathVariable("studentCode") String studentCode);
}
