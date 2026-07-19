package com.example.web.client;

import java.util.List;

/** The aggregated transcript from enrollment-service, as consumed by the UI. */
public class StudentEnrollmentsView {

    private String studentCode;
    private StudentView student;
    private List<EnrolledCourseView> enrollments;
    private int totalCourses;
    private int creditsEarned;
    private int creditsInProgress;
    private Double cumulativeGpa;
    private boolean partial;
    private List<String> warnings;

    public String getStudentCode() {
        return studentCode;
    }

    public void setStudentCode(String studentCode) {
        this.studentCode = studentCode;
    }

    public StudentView getStudent() {
        return student;
    }

    public void setStudent(StudentView student) {
        this.student = student;
    }

    public List<EnrolledCourseView> getEnrollments() {
        return enrollments;
    }

    public void setEnrollments(List<EnrolledCourseView> enrollments) {
        this.enrollments = enrollments;
    }

    public int getTotalCourses() {
        return totalCourses;
    }

    public void setTotalCourses(int totalCourses) {
        this.totalCourses = totalCourses;
    }

    public int getCreditsEarned() {
        return creditsEarned;
    }

    public void setCreditsEarned(int creditsEarned) {
        this.creditsEarned = creditsEarned;
    }

    public int getCreditsInProgress() {
        return creditsInProgress;
    }

    public void setCreditsInProgress(int creditsInProgress) {
        this.creditsInProgress = creditsInProgress;
    }

    public Double getCumulativeGpa() {
        return cumulativeGpa;
    }

    public void setCumulativeGpa(Double cumulativeGpa) {
        this.cumulativeGpa = cumulativeGpa;
    }

    public boolean isPartial() {
        return partial;
    }

    public void setPartial(boolean partial) {
        this.partial = partial;
    }

    public List<String> getWarnings() {
        return warnings;
    }

    public void setWarnings(List<String> warnings) {
        this.warnings = warnings;
    }
}
