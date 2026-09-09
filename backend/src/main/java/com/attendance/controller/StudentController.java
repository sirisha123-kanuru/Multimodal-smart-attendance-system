package com.attendance.controller;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.attendance.entity.Student;
import com.attendance.service.StudentService;
import com.fasterxml.jackson.databind.ObjectMapper;

@RestController
@RequestMapping("/students")
@CrossOrigin(origins = {
        "http://localhost:5173",
        "http://localhost:5174"
})
public class StudentController {

    @Autowired
    private StudentService studentService;

    // ==========================================
    // ADD STUDENT WITH PHOTO
    // ==========================================

    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public Student addStudent(
            @RequestPart("student") String studentJson,
            @RequestPart("photo") MultipartFile photo
    ) throws IOException {

        ObjectMapper mapper = new ObjectMapper();

        Student student = mapper.readValue(
                studentJson,
                Student.class
        );

        // ------------------------------------------
        // Create uploads/students folder
        // ------------------------------------------

        Path uploadPath = Paths.get(
                "uploads",
                "students"
        );

        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }

        // ------------------------------------------
        // Get original file name
        // ------------------------------------------

        String originalFileName =
                photo.getOriginalFilename();

        String extension = "";

        if (originalFileName != null
                && originalFileName.contains(".")) {

            extension = originalFileName.substring(
                    originalFileName.lastIndexOf(".")
            );
        }

        // ------------------------------------------
        // Create unique file name
        // ------------------------------------------

        String fileName =
                student.getRollNumber()
                        + "_"
                        + System.currentTimeMillis()
                        + extension;

        Path filePath =
                uploadPath.resolve(fileName);

        // ------------------------------------------
        // Save actual image
        // ------------------------------------------

        Files.copy(
                photo.getInputStream(),
                filePath,
                StandardCopyOption.REPLACE_EXISTING
        );

        // ------------------------------------------
        // Save photo path in database
        // ------------------------------------------

        student.setPhotoPath(
                "uploads/students/" + fileName
        );

        // ------------------------------------------
        // StudentService automatically assigns
        // the next available AI face label
        // ------------------------------------------

        return studentService.addStudent(student);
    }

    // ==========================================
    // GET ALL STUDENTS
    // ==========================================

    @GetMapping
    public List<Student> getAllStudents() {

        return studentService.getAllStudents();
    }

    // ==========================================
    // GET STUDENT BY DATABASE ID
    // ==========================================

    @GetMapping("/{id}")
    public Student getStudentById(
            @PathVariable Long id
    ) {

        return studentService.getStudentById(id);
    }

    // ==========================================
    // GET STUDENT BY AI FACE LABEL
    // ==========================================

    @GetMapping("/face-label/{faceLabel}")
    public Student getStudentByFaceLabel(
            @PathVariable Integer faceLabel
    ) {

        return studentService.getStudentByFaceLabel(
                faceLabel
        );
    }

    // ==========================================
    // UPDATE STUDENT
    // ==========================================

    @PutMapping("/{id}")
    public Student updateStudent(
            @PathVariable Long id,
            @RequestBody Student student
    ) {

        student.setId(id);

        return studentService.updateStudent(student);
    }

    // ==========================================
    // DELETE STUDENT
    // ==========================================

    @DeleteMapping("/{id}")
    public String deleteStudent(
            @PathVariable Long id
    ) {

        studentService.deleteStudent(id);

        return "Deleted Successfully";
    }
}