package com.example.enrollment.client;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cloud.openfeign.FallbackFactory;
import org.springframework.stereotype.Component;

/**
 * Fallback for {@link CourseClient}. When course-service cannot be reached we
 * still return a placeholder carrying the requested {@code courseCode} (with
 * null details), so the aggregation can show the code and flag that the course
 * details are unavailable rather than dropping the row entirely.
 */
@Component
public class CourseClientFallbackFactory implements FallbackFactory<CourseClient> {

    private static final Logger log = LoggerFactory.getLogger(CourseClientFallbackFactory.class);

    @Override
    public CourseClient create(Throwable cause) {
        return courseCode -> {
            log.warn("course-service unavailable for '{}', degrading: {}", courseCode, cause.toString());
            return new CourseDto(courseCode, null, null, null);
        };
    }
}
