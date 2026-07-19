package com.example.enrollment.repository;

import java.util.List;

import com.example.enrollment.domain.Enrollment;
import com.example.enrollment.domain.EnrollmentStatus;
import org.springframework.data.jpa.repository.JpaRepository;

public interface EnrollmentRepository extends JpaRepository<Enrollment, Long> {

    List<Enrollment> findByStudentCode(String studentCode);

    List<Enrollment> findByOfferingCode(String offeringCode);

    boolean existsByStudentCodeAndOfferingCodeAndStatus(
            String studentCode, String offeringCode, EnrollmentStatus status);
}
