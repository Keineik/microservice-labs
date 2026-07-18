package com.example.enrollment;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

/**
 * Enrollment Service - owns enrollment records and aggregates a student's
 * registrations by calling student-service and course-service through OpenFeign.
 *
 * <p>{@code @EnableFeignClients} activates the declarative Feign clients in the
 * {@code client} package.
 */
@SpringBootApplication
@EnableFeignClients
public class EnrollmentServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(EnrollmentServiceApplication.class, args);
    }
}
