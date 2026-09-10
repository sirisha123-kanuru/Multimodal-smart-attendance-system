package com.attendance.controller;

import com.attendance.entity.Faculty;
import com.attendance.service.FacultyService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/faculty")
@CrossOrigin(origins = {
        "http://localhost:5173",
        "http://localhost:5174",
        "https://multimodal-smart-attendance-system.vercel.app"
})
public class FacultyController {

    @Autowired
    private FacultyService facultyService;

    // Register Faculty
    @PostMapping("/register")
    public Faculty register(@RequestBody Faculty faculty) {
        return facultyService.registerFaculty(faculty);
    }

    // Login Faculty
    @PostMapping("/login")
    public Faculty login(@RequestBody Faculty faculty) {

        return facultyService.login(
                faculty.getFacultyId(),
                faculty.getPassword()
        );

    }

}
