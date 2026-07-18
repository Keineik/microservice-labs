package com.example.student;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Student Service - owns the student catalog.
 *
 * <p>The eureka-client starter on the classpath auto-registers this application
 * with the discovery server, so no {@code @EnableEurekaClient} annotation is
 * needed. Other services resolve it by its {@code spring.application.name}
 * ("student-service"), never by a hardcoded host/port.
 */
@SpringBootApplication
public class StudentServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(StudentServiceApplication.class, args);
    }
}
