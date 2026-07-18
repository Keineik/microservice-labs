package com.example.student.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/**
 * A student. {@code studentCode} is the stable business key that other services
 * (e.g. enrollment-service) use to reference a student across service
 * boundaries - they never share this table or its numeric primary key.
 */
@Entity
@Table(name = "students")
public class Student {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 20)
    private String studentCode;

    @Column(nullable = false, length = 200)
    private String fullName;

    @Column(nullable = false, unique = true, length = 255)
    private String email;

    @Column(length = 100)
    private String major;

    private Integer enrollmentYear;

    protected Student() {
        // Required by JPA.
    }

    public Student(String studentCode, String fullName, String email, String major, Integer enrollmentYear) {
        this.studentCode = studentCode;
        this.fullName = fullName;
        this.email = email;
        this.major = major;
        this.enrollmentYear = enrollmentYear;
    }

    public Long getId() {
        return id;
    }

    public String getStudentCode() {
        return studentCode;
    }

    public String getFullName() {
        return fullName;
    }

    public String getEmail() {
        return email;
    }

    public String getMajor() {
        return major;
    }

    public Integer getEnrollmentYear() {
        return enrollmentYear;
    }
}
