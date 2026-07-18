package com.example.course.web;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.course.dto.CourseResponse;
import com.example.course.error.ResourceNotFoundException;
import com.example.course.service.CourseService;
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

    @Test
    void detailReturnsCourse() throws Exception {
        when(service.getByCode("CS101")).thenReturn(
                new CourseResponse(1L, "CS101", "Introduction to Programming", 3, "Computer Science"));

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
}
