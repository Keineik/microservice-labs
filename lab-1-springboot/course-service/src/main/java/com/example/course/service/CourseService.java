package com.example.course.service;

import java.util.List;

import com.example.course.dto.CourseResponse;
import com.example.course.error.ResourceNotFoundException;
import com.example.course.repository.CourseRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class CourseService {

    private final CourseRepository repository;

    public CourseService(CourseRepository repository) {
        this.repository = repository;
    }

    @Transactional(readOnly = true)
    public List<CourseResponse> listAll() {
        return repository.findAll().stream().map(CourseResponse::from).toList();
    }

    @Transactional(readOnly = true)
    public CourseResponse getByCode(String courseCode) {
        return repository.findByCourseCode(courseCode)
                .map(CourseResponse::from)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "No course with code '" + courseCode + "'"));
    }
}
