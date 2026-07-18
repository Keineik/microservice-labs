package com.example.course.config;

import java.util.List;

import com.example.course.domain.Course;
import com.example.course.repository.CourseRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Seeds the course catalog on startup. These course codes are the ones
 * referenced by enrollment-service's seed data.
 */
@Configuration
public class DataSeeder {

    @Bean
    CommandLineRunner seedCourses(CourseRepository repository) {
        return args -> {
            if (repository.count() > 0) {
                return;
            }
            repository.saveAll(List.of(
                    new Course("CS101", "Introduction to Programming", 3, "Computer Science"),
                    new Course("CS102", "Data Structures and Algorithms", 4, "Computer Science"),
                    new Course("CS201", "Operating Systems", 3, "Computer Science"),
                    new Course("CS202", "Database Systems", 3, "Computer Science"),
                    new Course("CS301", "Distributed Systems", 3, "Computer Science"),
                    new Course("SE201", "Software Engineering", 3, "Software Engineering"),
                    new Course("IS101", "Information Systems Fundamentals", 3, "Information Systems"),
                    new Course("MATH101", "Calculus I", 4, "Mathematics"),
                    new Course("MATH201", "Linear Algebra", 3, "Mathematics"),
                    new Course("DS201", "Introduction to Data Science", 3, "Data Science")));
        };
    }
}
