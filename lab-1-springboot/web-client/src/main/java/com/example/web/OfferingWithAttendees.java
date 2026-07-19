package com.example.web;

import java.util.List;

import com.example.web.client.AttendeeView;
import com.example.web.client.OfferingView;

/**
 * View helper for the course-detail page: one offering together with the
 * students attending it. Assembled in the controller (the template cannot call
 * services) from a course-service offering + an enrollment-service attendees
 * lookup.
 */
public class OfferingWithAttendees {

    private OfferingView offering;
    private List<AttendeeView> attendees;
    private boolean partial;

    public OfferingView getOffering() {
        return offering;
    }

    public void setOffering(OfferingView offering) {
        this.offering = offering;
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
}
