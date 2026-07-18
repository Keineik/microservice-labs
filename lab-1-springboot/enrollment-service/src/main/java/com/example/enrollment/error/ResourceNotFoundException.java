package com.example.enrollment.error;

/** Thrown when a referenced resource genuinely does not exist -> HTTP 404. */
public class ResourceNotFoundException extends RuntimeException {

    public ResourceNotFoundException(String message) {
        super(message);
    }
}
