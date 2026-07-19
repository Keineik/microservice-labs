package com.example.enrollment.client;

import java.util.Arrays;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cloud.openfeign.FallbackFactory;
import org.springframework.stereotype.Component;

/**
 * Fallback for {@link OfferingClient}. When course-service is unreachable we
 * return a placeholder derived from the offeringCode itself (which encodes
 * course/year/semester/section), leaving the course title/credits null. The
 * aggregation can then still show the course code and term and flag the row as
 * having incomplete details, rather than dropping it.
 */
@Component
public class OfferingClientFallbackFactory implements FallbackFactory<OfferingClient> {

    private static final Logger log = LoggerFactory.getLogger(OfferingClientFallbackFactory.class);

    @Override
    public OfferingClient create(Throwable cause) {
        return offeringCode -> {
            log.warn("course-service unavailable for offering '{}', degrading: {}",
                    offeringCode, cause.toString());
            return placeholder(offeringCode);
        };
    }

    /** Parse "{courseCode}-{year}-{semester}-{section}" as far as possible. */
    static OfferingDto placeholder(String offeringCode) {
        String courseCode = null;
        Integer year = null;
        Integer semester = null;
        String section = null;
        String[] parts = offeringCode.split("-");
        if (parts.length >= 4) {
            section = parts[parts.length - 1];
            semester = tryParse(parts[parts.length - 2]);
            year = tryParse(parts[parts.length - 3]);
            courseCode = String.join("-", Arrays.copyOfRange(parts, 0, parts.length - 3));
        }
        return new OfferingDto(offeringCode, courseCode, null, null, null, year, semester, section, null);
    }

    private static Integer tryParse(String value) {
        try {
            return Integer.valueOf(value);
        } catch (NumberFormatException ex) {
            return null;
        }
    }
}
