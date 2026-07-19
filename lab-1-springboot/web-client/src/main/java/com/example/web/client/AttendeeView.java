package com.example.web.client;

/** One student attending an offering (from enrollment-service's attendees view). */
public class AttendeeView {

    private String studentCode;
    private String fullName;
    private String major;
    private String status;
    private Double grade;
    private boolean studentAvailable;

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

    public String getMajor() {
        return major;
    }

    public void setMajor(String major) {
        this.major = major;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Double getGrade() {
        return grade;
    }

    public void setGrade(Double grade) {
        this.grade = grade;
    }

    public boolean isStudentAvailable() {
        return studentAvailable;
    }

    public void setStudentAvailable(boolean studentAvailable) {
        this.studentAvailable = studentAvailable;
    }
}
