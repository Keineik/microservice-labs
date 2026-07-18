package com.example.discovery;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.netflix.eureka.server.EnableEurekaServer;

/**
 * Eureka discovery server.
 *
 * <p>This is the service registry. Every other service registers itself here on
 * startup and looks up peers <em>by name</em> (never by a hardcoded URL). The
 * dashboard is served at the root path (http://localhost:8761).
 */
@SpringBootApplication
@EnableEurekaServer
public class DiscoveryServerApplication {

    public static void main(String[] args) {
        SpringApplication.run(DiscoveryServerApplication.class, args);
    }
}
