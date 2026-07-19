package com.example.web.client;

/**
 * Backing bean for the add-student form and the JSON body sent to student-service.
 * A mutable JavaBean so Thymeleaf can bind form fields and Jackson can serialize
 * it; the field names match student-service's CreateStudentRequest.
 */
public class StudentForm {

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
