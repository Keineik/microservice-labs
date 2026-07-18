package com.example.enrollment.error;

/** Thrown when an enrollment would duplicate an active one -> HTTP 409. */
public class DuplicateResourceException extends RuntimeException {

    public DuplicateResourceException(String message) {
        super(message);
    }
}
