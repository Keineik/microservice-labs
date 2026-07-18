package com.example.student.error;

/** Thrown when a student would violate a uniqueness rule -> mapped to HTTP 409. */
public class DuplicateResourceException extends RuntimeException {

    public DuplicateResourceException(String message) {
        super(message);
    }
}
