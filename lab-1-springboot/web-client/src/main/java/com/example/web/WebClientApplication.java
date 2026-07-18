package com.example.web;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

/**
 * Web Client - a server-rendered Thymeleaf UI. It has no database; it reads
 * everything from student-service and enrollment-service over Feign, resolving
 * them by name via Eureka.
 */
@SpringBootApplication
@EnableFeignClients
public class WebClientApplication {

    public static void main(String[] args) {
        SpringApplication.run(WebClientApplication.class, args);
    }
}
