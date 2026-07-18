package com.example.course.error;

/** Thrown when a requested course does not exist -> mapped to HTTP 404. */
public class ResourceNotFoundException extends RuntimeException {

    public ResourceNotFoundException(String message) {
        super(message);
    }
}
