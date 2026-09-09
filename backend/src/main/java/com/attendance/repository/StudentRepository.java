package com.attendance.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.attendance.entity.Student;

@Repository
public interface StudentRepository extends JpaRepository<Student, Long> {

    // Find student using AI face-recognition label
    Optional<Student> findByFaceLabel(Integer faceLabel);
}