package com.example.web.client;

import java.util.List;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

/** Feign client for student-service, resolved by name via Eureka. */
@FeignClient(name = "student-service", path = "/api/students")
public interface StudentClient {

    @GetMapping
    List<StudentView> list();

    @PostMapping
    StudentView create(@RequestBody StudentForm form);
}
