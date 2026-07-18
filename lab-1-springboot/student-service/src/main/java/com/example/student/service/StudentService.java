package com.example.student.service;

import java.util.List;

import com.example.student.domain.Student;
import com.example.student.dto.CreateStudentRequest;
import com.example.student.dto.StudentResponse;
import com.example.student.error.DuplicateResourceException;
import com.example.student.error.ResourceNotFoundException;
import com.example.student.repository.StudentRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class StudentService {

    private final StudentRepository repository;

    public StudentService(StudentRepository repository) {
        this.repository = repository;
    }

    @Transactional(readOnly = true)
    public List<StudentResponse> listAll() {
        return repository.findAll().stream().map(StudentResponse::from).toList();
    }

    @Transactional(readOnly = true)
    public StudentResponse getByCode(String studentCode) {
        return repository.findByStudentCode(studentCode)
                .map(StudentResponse::from)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "No student with code '" + studentCode + "'"));
    }

    @Transactional
    public StudentResponse create(CreateStudentRequest request) {
        if (repository.existsByStudentCode(request.studentCode())) {
            throw new DuplicateResourceException(
                    "Student code '" + request.studentCode() + "' is already taken");
        }
        if (repository.existsByEmail(request.email())) {
            throw new DuplicateResourceException(
                    "Email '" + request.email() + "' is already registered");
        }
        Student saved = repository.save(new Student(
                request.studentCode(),
                request.fullName(),
                request.email(),
                request.major(),
                request.enrollmentYear()));
        return StudentResponse.from(saved);
    }
}
