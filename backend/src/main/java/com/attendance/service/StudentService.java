package com.attendance.service;

import com.attendance.entity.Student;
import com.attendance.repository.StudentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class StudentService {

    @Autowired
    private StudentRepository studentRepository;

    // ==========================================
    // ADD STUDENT
    // ==========================================

    public Student addStudent(Student student) {

        /*
         * AI face labels are separate from the
         * student's actual roll number.
         *
         * Example:
         *
         * faceLabel = 1
         * rollNumber = 23CS101
         *
         * faceLabel = 2
         * rollNumber = 23CS102
         */

        if (student.getFaceLabel() == null) {

            List<Student> students = studentRepository.findAll();

            int nextLabel = 1;

            for (Student existingStudent : students) {

                if (existingStudent.getFaceLabel() != null
                        && existingStudent.getFaceLabel() >= nextLabel) {

                    nextLabel = existingStudent.getFaceLabel() + 1;
                }
            }

            student.setFaceLabel(nextLabel);
        }

        return studentRepository.save(student);
    }

    // ==========================================
    // GET ALL STUDENTS
    // ==========================================

    public List<Student> getAllStudents() {

        return studentRepository.findAll();
    }

    // ==========================================
    // GET STUDENT BY ID
    // ==========================================

    public Student getStudentById(Long id) {

        return studentRepository
                .findById(id)
                .orElse(null);
    }

    // ==========================================
    // FIND STUDENT BY AI FACE LABEL
    // ==========================================

    public Student getStudentByFaceLabel(Integer faceLabel) {

        return studentRepository
                .findByFaceLabel(faceLabel)
                .orElse(null);
    }

    // ==========================================
    // UPDATE STUDENT
    // ==========================================

    public Student updateStudent(Student student) {

        return studentRepository.save(student);
    }

    // ==========================================
    // DELETE STUDENT
    // ==========================================

    public void deleteStudent(Long id) {

        studentRepository.deleteById(id);
    }
}