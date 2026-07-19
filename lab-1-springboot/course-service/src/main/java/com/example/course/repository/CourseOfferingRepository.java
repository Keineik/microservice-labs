package com.example.course.repository;

import java.util.List;
import java.util.Optional;

import com.example.course.domain.CourseOffering;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CourseOfferingRepository extends JpaRepository<CourseOffering, Long> {

    Optional<CourseOffering> findByOfferingCode(String offeringCode);

    List<CourseOffering> findByCourseCodeOrderByYearAscSemesterAscSectionAsc(String courseCode);
}
