package com.example.student.config;

import java.util.List;

import com.example.student.domain.Student;
import com.example.student.repository.StudentRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Seeds the in-memory database on startup so the service has data to serve
 * without any manual setup. The student codes here are the same ones referenced
 * by enrollment-service's seed data, so cross-service lookups resolve.
 */
@Configuration
public class DataSeeder {

    @Bean
    CommandLineRunner seedStudents(StudentRepository repository) {
        return args -> {
            if (repository.count() > 0) {
                return;
            }
            repository.saveAll(List.of(
                    new Student("SV001", "Nguyen Van An", "an.nguyen@example.edu", "Computer Science", 2022),
                    new Student("SV002", "Tran Thi Binh", "binh.tran@example.edu", "Computer Science", 2022),
                    new Student("SV003", "Le Van Cuong", "cuong.le@example.edu", "Information Systems", 2023),
                    new Student("SV004", "Pham Thi Dung", "dung.pham@example.edu", "Software Engineering", 2023),
                    new Student("SV005", "Hoang Van Em", "em.hoang@example.edu", "Computer Science", 2021),
                    new Student("SV006", "Vo Thi Hoa", "hoa.vo@example.edu", "Data Science", 2024),
                    new Student("SV007", "Dang Van Khoa", "khoa.dang@example.edu", "Software Engineering", 2022),
                    new Student("SV008", "Bui Thi Lan", "lan.bui@example.edu", "Information Systems", 2024)));
        };
    }
}
