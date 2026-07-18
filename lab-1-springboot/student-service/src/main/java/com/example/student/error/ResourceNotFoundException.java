package com.example.student.error;

/** Thrown when a requested student does not exist -> mapped to HTTP 404. */
public class ResourceNotFoundException extends RuntimeException {

    public ResourceNotFoundException(String message) {
        super(message);
    }
}
