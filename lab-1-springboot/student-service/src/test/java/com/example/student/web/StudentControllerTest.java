package com.example.student.web;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.List;

import com.example.student.dto.StudentResponse;
import com.example.student.error.ResourceNotFoundException;
import com.example.student.service.StudentService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

/**
 * Slice test of the web layer only (no DB, no Eureka). The service is mocked so
 * we assert HTTP mapping and error translation, not persistence.
 */
@WebMvcTest(controllers = StudentController.class)
@TestPropertySource(properties = "eureka.client.enabled=false")
class StudentControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private StudentService service;

    @Test
    void listReturnsStudents() throws Exception {
        when(service.listAll()).thenReturn(List.of(
                new StudentResponse(1L, "SV001", "Nguyen Van An", "an.nguyen@example.edu",
                        "Computer Science", 2022)));

        mockMvc.perform(get("/api/students"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].studentCode").value("SV001"))
                .andExpect(jsonPath("$[0].fullName").value("Nguyen Van An"));
    }

    @Test
    void unknownStudentReturns404ProblemDetail() throws Exception {
        when(service.getByCode("SV999"))
                .thenThrow(new ResourceNotFoundException("No student with code 'SV999'"));

        mockMvc.perform(get("/api/students/SV999"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.title").value("Resource not found"));
    }
}
