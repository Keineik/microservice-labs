package com.example.web.client;

import java.util.List;

/** The attendees of one offering (from enrollment-service). */
public class OfferingAttendeesView {

    private String offeringCode;
    private List<AttendeeView> attendees;
    private boolean partial;
    private List<String> warnings;

    public String getOfferingCode() {
        return offeringCode;
    }

    public void setOfferingCode(String offeringCode) {
        this.offeringCode = offeringCode;
    }

    public List<AttendeeView> getAttendees() {
        return attendees;
    }

    public void setAttendees(List<AttendeeView> attendees) {
        this.attendees = attendees;
    }

    public boolean isPartial() {
        return partial;
    }

    public void setPartial(boolean partial) {
        this.partial = partial;
    }

    public List<String> getWarnings() {
        return warnings;
    }

    public void setWarnings(List<String> warnings) {
        this.warnings = warnings;
    }
}
