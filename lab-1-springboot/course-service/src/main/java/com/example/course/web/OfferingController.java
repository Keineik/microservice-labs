package com.example.course.web;

import com.example.course.dto.OfferingResponse;
import com.example.course.service.OfferingService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/offerings")
public class OfferingController {

    private final OfferingService service;

    public OfferingController(OfferingService service) {
        this.service = service;
    }

    /** Get one offering (with course details) by its business key. */
    @GetMapping("/{offeringCode}")
    public OfferingResponse getByCode(@PathVariable("offeringCode") String offeringCode) {
        return service.getByOfferingCode(offeringCode);
    }
}
