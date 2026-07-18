package com.example.web.client;

import java.util.List;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;

/** Feign client for student-service, resolved by name via Eureka. */
@FeignClient(name = "student-service", path = "/api/students")
public interface StudentClient {

    @GetMapping
    List<StudentView> list();
}
