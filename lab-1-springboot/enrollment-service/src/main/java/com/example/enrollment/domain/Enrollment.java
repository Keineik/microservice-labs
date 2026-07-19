package com.example.enrollment.domain;

import java.time.Instant;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Table;

/**
 * A student's registration in a course offering.
 *
 * <p>There are no foreign keys to student or offering: those live in other
 * services and other databases. This service stores only the business keys
 * ({@code studentCode}, {@code offeringCode}) and resolves the human-readable
 * details at read time by calling student-service and course-service. The
 * offeringCode encodes the course, year, semester and section.
 */
@Entity
@Table(name = "enrollments", indexes = {
        @Index(name = "idx_enrollment_student", columnList = "studentCode"),
        @Index(name = "idx_enrollment_offering", columnList = "offeringCode")
})
public class Enrollment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 20)
    private String studentCode;

    @Column(nullable = false, length = 40)
    private String offeringCode;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private EnrollmentStatus status;

    private Double grade;

    @Column(nullable = false)
    private Instant registeredAt;

    protected Enrollment() {
        // Required by JPA.
    }

    public Enrollment(String studentCode, String offeringCode, EnrollmentStatus status, Double grade) {
        this.studentCode = studentCode;
        this.offeringCode = offeringCode;
        this.status = status;
        this.grade = grade;
        this.registeredAt = Instant.now();
    }

    public Long getId() {
        return id;
    }

    public String getStudentCode() {
        return studentCode;
    }

    public String getOfferingCode() {
        return offeringCode;
    }

    public EnrollmentStatus getStatus() {
        return status;
    }

    public Double getGrade() {
        return grade;
    }

    public Instant getRegisteredAt() {
        return registeredAt;
    }
}
