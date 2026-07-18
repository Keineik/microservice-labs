package com.example.enrollment.repository;

import java.util.List;

import com.example.enrollment.domain.Enrollment;
import com.example.enrollment.domain.EnrollmentStatus;
import org.springframework.data.jpa.repository.JpaRepository;

public interface EnrollmentRepository extends JpaRepository<Enrollment, Long> {

    List<Enrollment> findByStudentCode(String studentCode);

    boolean existsByStudentCodeAndCourseCodeAndStatus(
            String studentCode, String courseCode, EnrollmentStatus status);
}
