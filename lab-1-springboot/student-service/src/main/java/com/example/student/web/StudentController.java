package com.example.student.web;

import java.net.URI;
import java.util.List;

import com.example.student.dto.CreateStudentRequest;
import com.example.student.dto.StudentResponse;
import com.example.student.service.StudentService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.util.UriComponentsBuilder;

@RestController
@RequestMapping("/api/students")
public class StudentController {

    private final StudentService service;

    public StudentController(StudentService service) {
        this.service = service;
    }

    /** List all students. */
    @GetMapping
    public List<StudentResponse> list() {
        return service.listAll();
    }

    /** Get one student by its business key (studentCode). */
    @GetMapping("/{studentCode}")
    public StudentResponse getByCode(@PathVariable String studentCode) {
        return service.getByCode(studentCode);
    }

    /** Create a student; returns 201 with a Location header. */
    @PostMapping
    public ResponseEntity<StudentResponse> create(
            @Valid @RequestBody CreateStudentRequest request,
            UriComponentsBuilder uriBuilder) {
        StudentResponse created = service.create(request);
        URI location = uriBuilder.path("/api/students/{code}")
                .buildAndExpand(created.studentCode())
                .toUri();
        return ResponseEntity.created(location).body(created);
    }
}
