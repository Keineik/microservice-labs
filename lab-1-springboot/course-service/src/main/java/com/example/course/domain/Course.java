package com.example.course.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;

/**
 * A course catalog entry. {@code courseCode} is the business key other services
 * use to reference a course. A course is opened for enrollment as one or more
 * {@link CourseOffering}s (per year/semester/section).
 */
@Entity
@Table(name = "courses")
public class Course {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 20)
    private String courseCode;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(nullable = false)
    private int credits;

    @Column(length = 100)
    private String department;

    @Lob
    private String description;

    protected Course() {
        // Required by JPA.
    }

    public Course(String courseCode, String title, int credits, String department, String description) {
        this.courseCode = courseCode;
        this.title = title;
        this.credits = credits;
        this.department = department;
        this.description = description;
    }

    public Long getId() {
        return id;
    }

    public String getCourseCode() {
        return courseCode;
    }

    public String getTitle() {
        return title;
    }

    public int getCredits() {
        return credits;
    }

    public String getDepartment() {
        return department;
    }

    public String getDescription() {
        return description;
    }
}
