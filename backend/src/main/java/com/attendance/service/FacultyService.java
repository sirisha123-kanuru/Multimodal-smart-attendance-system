package com.attendance.service;

import com.attendance.entity.Faculty;
import com.attendance.repository.FacultyRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class FacultyService {

    @Autowired
    private FacultyRepository facultyRepository;

    // Register Faculty
    public Faculty registerFaculty(Faculty faculty) {
        return facultyRepository.save(faculty);
    }

    // Login Faculty
    public Faculty login(String facultyId, String password) {

        Faculty faculty = facultyRepository.findByFacultyId(facultyId);

        if (faculty != null &&
                faculty.getPassword().equals(password)) {

            return faculty;
        }

        return null;
    }

}