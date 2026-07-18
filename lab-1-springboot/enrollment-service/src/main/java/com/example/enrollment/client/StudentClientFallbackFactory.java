package com.example.enrollment.client;

import com.example.enrollment.error.ResourceNotFoundException;
import feign.FeignException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cloud.openfeign.FallbackFactory;
import org.springframework.stereotype.Component;

/**
 * Fallback for {@link StudentClient}. A {@link FallbackFactory} (rather than a
 * plain fallback) gives us the failure cause, so we can tell two cases apart:
 *
 * <ul>
 *   <li>a real 404 (the student genuinely does not exist) -> rethrow as a 404,
 *       so the caller gets an honest "not found";</li>
 *   <li>any other failure (timeout, connection refused, open circuit) ->
 *       return {@code null}, letting the aggregation continue in a degraded
 *       (partial) mode instead of failing outright.</li>
 * </ul>
 */
@Component
public class StudentClientFallbackFactory implements FallbackFactory<StudentClient> {

    private static final Logger log = LoggerFactory.getLogger(StudentClientFallbackFactory.class);

    @Override
    public StudentClient create(Throwable cause) {
        return studentCode -> {
            if (cause instanceof FeignException.NotFound) {
                throw new ResourceNotFoundException("No student with code '" + studentCode + "'");
            }
            log.warn("student-service unavailable for '{}', degrading: {}", studentCode, cause.toString());
            return null;
        };
    }
}
