package com.example.web.client;

/**
 * The web client's view of a student (from student-service).
 *
 * <p>A plain JavaBean (not a record) on purpose: Thymeleaf resolves properties
 * through SpEL, which reads {@code getX()} getters reliably but does not always
 * resolve a record's {@code x()} accessor. Jackson populates it via setters.
 */
public class StudentView {

    private String studentCode;
    private String fullName;
    private String email;
    private String major;
    private Integer enrollmentYear;

    public String getStudentCode() {
        return studentCode;
    }

    public void setStudentCode(String studentCode) {
        this.studentCode = studentCode;
    }

    public String getFullName() {
        return fullName;
    }

    public void setFullName(String fullName) {
        this.fullName = fullName;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getMajor() {
        return major;
    }

    public void setMajor(String major) {
        this.major = major;
    }

    public Integer getEnrollmentYear() {
        return enrollmentYear;
    }

    public void setEnrollmentYear(Integer enrollmentYear) {
        this.enrollmentYear = enrollmentYear;
    }
}
