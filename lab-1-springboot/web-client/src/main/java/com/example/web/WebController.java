package com.example.web;

import java.util.List;

import com.example.web.client.EnrollmentClient;
import com.example.web.client.StudentClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

/**
 * Renders the two pages: a list of students, and one student's enrolled courses.
 * Downstream failures are caught here so the UI degrades to a friendly message
 * instead of an error page.
 */
@Controller
public class WebController {

    private static final Logger log = LoggerFactory.getLogger(WebController.class);

    private final StudentClient studentClient;
    private final EnrollmentClient enrollmentClient;

    public WebController(StudentClient studentClient, EnrollmentClient enrollmentClient) {
        this.studentClient = studentClient;
        this.enrollmentClient = enrollmentClient;
    }

    /** Home page: the list of students. */
    @GetMapping("/")
    public String index(Model model) {
        try {
            model.addAttribute("students", studentClient.list());
        } catch (Exception ex) {
            log.warn("Could not load students: {}", ex.toString());
            model.addAttribute("students", List.of());
            model.addAttribute("error", "student-service is unavailable right now. Please try again shortly.");
        }
        return "students";
    }

    /** Detail page: a student and the courses they are enrolled in. */
    @GetMapping("/students/{studentCode}")
    public String studentDetail(@PathVariable String studentCode, Model model) {
        model.addAttribute("studentCode", studentCode);
        try {
            model.addAttribute("data", enrollmentClient.getStudentEnrollments(studentCode));
        } catch (Exception ex) {
            log.warn("Could not load enrollments for {}: {}", studentCode, ex.toString());
            model.addAttribute("error",
                    "Could not load enrollment data for " + studentCode
                            + " (enrollment-service may be unavailable).");
        }
        return "student";
    }
}
