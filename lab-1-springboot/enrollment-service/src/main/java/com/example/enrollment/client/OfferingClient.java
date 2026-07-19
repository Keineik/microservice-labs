package com.example.enrollment.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

/**
 * OpenFeign client for course-service's offering endpoint, resolved by name via
 * Eureka. Returns the offering joined with its course details.
 */
@FeignClient(
        name = "course-service",
        path = "/api/offerings",
        fallbackFactory = OfferingClientFallbackFactory.class)
public interface OfferingClient {

    @GetMapping("/{offeringCode}")
    OfferingDto getByCode(@PathVariable("offeringCode") String offeringCode);
}
