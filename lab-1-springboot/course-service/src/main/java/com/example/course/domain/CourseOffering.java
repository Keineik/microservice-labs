package com.example.course.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Table;

/**
 * A course opened for enrollment in a specific year + semester + section - the
 * concrete thing a student registers for. {@code offeringCode} is the stable
 * business key (e.g. "CS101-2024-1-01") that enrollment-service references.
 *
 * <p>Kept deliberately lean (no capacity/schedule/registration window): the lab
 * is about service discovery and inter-service communication, not registration
 * rules.
 */
@Entity
@Table(name = "course_offerings",
        indexes = @Index(name = "idx_offering_course", columnList = "courseCode"))
public class CourseOffering {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 40)
    private String offeringCode;

    @Column(nullable = false, length = 20)
    private String courseCode;

    // "year" is a reserved word in SQL/H2, so map it to a safe column name.
    @Column(name = "academic_year", nullable = false)
    private int year;

    /** Semester within the academic year: 1, 2 or 3 (displayed as HK1/HK2/HK3). */
    @Column(nullable = false)
    private int semester;

    @Column(nullable = false, length = 10)
    private String section;

    @Column(length = 200)
    private String instructor;

    protected CourseOffering() {
        // Required by JPA.
    }

    public CourseOffering(String courseCode, int year, int semester, String section, String instructor) {
        this.courseCode = courseCode;
        this.year = year;
        this.semester = semester;
        this.section = section;
        this.instructor = instructor;
        this.offeringCode = buildCode(courseCode, year, semester, section);
    }

    /** Business key format: {courseCode}-{year}-{semester}-{section}. */
    public static String buildCode(String courseCode, int year, int semester, String section) {
        return courseCode + "-" + year + "-" + semester + "-" + section;
    }

    public Long getId() {
        return id;
    }

    public String getOfferingCode() {
        return offeringCode;
    }

    public String getCourseCode() {
        return courseCode;
    }

    public int getYear() {
        return year;
    }

    public int getSemester() {
        return semester;
    }

    public String getSection() {
        return section;
    }

    public String getInstructor() {
        return instructor;
    }
}
