package com.example.web;

import java.util.ArrayList;
import java.util.List;

import com.example.web.client.CourseClient;
import com.example.web.client.CourseView;
import com.example.web.client.EnrollmentClient;
import com.example.web.client.OfferingAttendeesView;
import com.example.web.client.OfferingView;
import com.example.web.client.StudentClient;
import com.example.web.client.StudentForm;
import com.example.web.client.StudentView;
import feign.FeignException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;

/**
 * The registrar ("giáo vụ") console: browse students and courses, view a
 * student's transcript (with GPA/credits) and a course's offerings + attendees,
 * and add a student. Everything is read from the services over Feign; downstream
 * failures are caught here so the UI degrades to a message instead of erroring.
 */
@Controller
public class WebController {

    private static final Logger log = LoggerFactory.getLogger(WebController.class);

    private final StudentClient studentClient;
    private final CourseClient courseClient;
    private final EnrollmentClient enrollmentClient;

    public WebController(StudentClient studentClient, CourseClient courseClient,
                         EnrollmentClient enrollmentClient) {
        this.studentClient = studentClient;
        this.courseClient = courseClient;
        this.enrollmentClient = enrollmentClient;
    }

    @GetMapping("/")
    public String home() {
        return "redirect:/students";
    }

    // ---- Students ----------------------------------------------------------

    @GetMapping("/students")
    public String students(Model model) {
        try {
            model.addAttribute("students", studentClient.list());
        } catch (Exception ex) {
            log.warn("Could not load students: {}", ex.toString());
            model.addAttribute("students", List.of());
            model.addAttribute("error", "student-service không sẵn sàng. Vui lòng thử lại sau.");
        }
        return "students";
    }

    @GetMapping("/students/new")
    public String newStudentForm(Model model) {
        if (!model.containsAttribute("studentForm")) {
            model.addAttribute("studentForm", new StudentForm());
        }
        return "student-form";
    }

    @PostMapping("/students")
    public String createStudent(@ModelAttribute StudentForm studentForm, Model model) {
        try {
            StudentView created = studentClient.create(studentForm);
            return "redirect:/students/" + created.getStudentCode();
        } catch (FeignException.Conflict ex) {
            model.addAttribute("error", "Mã sinh viên hoặc email đã tồn tại.");
        } catch (FeignException.BadRequest ex) {
            model.addAttribute("error", "Dữ liệu không hợp lệ. Vui lòng kiểm tra lại các trường.");
        } catch (Exception ex) {
            log.warn("Could not create student: {}", ex.toString());
            model.addAttribute("error", "Không thể thêm sinh viên (student-service có thể không sẵn sàng).");
        }
        model.addAttribute("studentForm", studentForm);
        return "student-form";
    }

    @GetMapping("/students/{studentCode}")
    public String studentDetail(@PathVariable String studentCode, Model model) {
        model.addAttribute("studentCode", studentCode);
        try {
            model.addAttribute("data", enrollmentClient.getStudentEnrollments(studentCode));
        } catch (FeignException.NotFound ex) {
            model.addAttribute("error", "Không tìm thấy sinh viên " + studentCode + ".");
        } catch (Exception ex) {
            log.warn("Could not load transcript for {}: {}", studentCode, ex.toString());
            model.addAttribute("error", "Không tải được dữ liệu đăng ký (service có thể không sẵn sàng).");
        }
        return "student";
    }

    // ---- Courses -----------------------------------------------------------

    @GetMapping("/courses")
    public String courses(Model model) {
        try {
            model.addAttribute("courses", courseClient.list());
        } catch (Exception ex) {
            log.warn("Could not load courses: {}", ex.toString());
            model.addAttribute("courses", List.of());
            model.addAttribute("error", "course-service không sẵn sàng. Vui lòng thử lại sau.");
        }
        return "courses";
    }

    @GetMapping("/courses/{courseCode}")
    public String courseDetail(@PathVariable String courseCode, Model model) {
        model.addAttribute("courseCode", courseCode);
        try {
            CourseView course = courseClient.getByCode(courseCode);
            model.addAttribute("course", course);
            model.addAttribute("offerings", loadOfferingsWithAttendees(courseCode));
        } catch (FeignException.NotFound ex) {
            model.addAttribute("error", "Không tìm thấy học phần " + courseCode + ".");
        } catch (Exception ex) {
            log.warn("Could not load course {}: {}", courseCode, ex.toString());
            model.addAttribute("error", "Không tải được dữ liệu học phần (service có thể không sẵn sàng).");
        }
        return "course";
    }

    /** For each offering of the course, fetch its attendees (degrading per offering). */
    private List<OfferingWithAttendees> loadOfferingsWithAttendees(String courseCode) {
        List<OfferingWithAttendees> items = new ArrayList<>();
        for (OfferingView offering : courseClient.offerings(courseCode)) {
            OfferingWithAttendees item = new OfferingWithAttendees();
            item.setOffering(offering);
            try {
                OfferingAttendeesView attendees =
                        enrollmentClient.getOfferingAttendees(offering.getOfferingCode());
                item.setAttendees(attendees.getAttendees());
                item.setPartial(attendees.isPartial());
            } catch (Exception ex) {
                log.warn("Could not load attendees for {}: {}", offering.getOfferingCode(), ex.toString());
                item.setAttendees(List.of());
                item.setPartial(true);
            }
            items.add(item);
        }
        return items;
    }
}
