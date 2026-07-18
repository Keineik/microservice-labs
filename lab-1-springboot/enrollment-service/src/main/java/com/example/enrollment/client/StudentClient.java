package com.example.enrollment.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

/**
 * OpenFeign client for student-service. The {@code name} is the logical service
 * name registered in Eureka; there is no host or port here - the load balancer
 * resolves an instance at call time. {@code fallbackFactory} supplies a graceful
 * degradation path (and access to the failure cause) when the call fails.
 */
@FeignClient(
        name = "student-service",
        path = "/api/students",
        fallbackFactory = StudentClientFallbackFactory.class)
public interface StudentClient {

    @GetMapping("/{studentCode}")
    StudentDto getByCode(@PathVariable("studentCode") String studentCode);
}
