package com.example.enrollment.domain;

/** Lifecycle of an enrollment. */
public enum EnrollmentStatus {
    /** Active registration in the current/most recent term. */
    REGISTERED,
    /** Finished, carries a grade. */
    COMPLETED,
    /** Cancelled before completion. */
    DROPPED
}
