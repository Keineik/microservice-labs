package com.example.course;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Course Service - owns the course catalog. Registers with Eureka as
 * "course-service" and is called by enrollment-service to resolve course
 * details for a student's registrations.
 */
@SpringBootApplication
public class CourseServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(CourseServiceApplication.class, args);
    }
}
