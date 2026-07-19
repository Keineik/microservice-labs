package com.example.course.web;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.List;

import com.example.course.dto.CourseResponse;
import com.example.course.dto.OfferingResponse;
import com.example.course.error.ResourceNotFoundException;
import com.example.course.service.CourseService;
import com.example.course.service.OfferingService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(controllers = CourseController.class)
@TestPropertySource(properties = "eureka.client.enabled=false")
class CourseControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private CourseService service;

    @MockitoBean
    private OfferingService offeringService;

    @Test
    void detailReturnsCourse() throws Exception {
        when(service.getByCode("CS101")).thenReturn(new CourseResponse(
                1L, "CS101", "Introduction to Programming", 3, "Computer Science", "Nhập môn lập trình."));

        mockMvc.perform(get("/api/courses/CS101"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.courseCode").value("CS101"))
                .andExpect(jsonPath("$.credits").value(3));
    }

    @Test
    void unknownCourseReturns404() throws Exception {
        when(service.getByCode("XX000"))
                .thenThrow(new ResourceNotFoundException("No course with code 'XX000'"));

        mockMvc.perform(get("/api/courses/XX000"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.title").value("Resource not found"));
    }

    @Test
    void listsOfferingsOfACourse() throws Exception {
        when(offeringService.getByCourseCode("CS101")).thenReturn(List.of(
                new OfferingResponse("CS101-2024-1-01", "CS101", "Introduction to Programming",
                        3, "Computer Science", 2024, 1, "01", "TS. Le Minh Hoang"),
                new OfferingResponse("CS101-2025-1-01", "CS101", "Introduction to Programming",
                        3, "Computer Science", 2025, 1, "01", "TS. Le Minh Hoang")));

        mockMvc.perform(get("/api/courses/CS101/offerings"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].offeringCode").value("CS101-2024-1-01"))
                .andExpect(jsonPath("$[1].year").value(2025));
    }
}
