package com.attendance.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "students")
public class Student {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String rollNumber;

    private String name;

    private String email;

    private String department;

    private String year;

    private String section;

    private String photoPath;

    // AI Face Recognition Label
    private Integer faceLabel;

    // ==========================================
    // DEFAULT CONSTRUCTOR
    // ==========================================

    public Student() {
    }

    // ==========================================
    // FULL CONSTRUCTOR
    // ==========================================

    public Student(
            Long id,
            String rollNumber,
            String name,
            String email,
            String department,
            String year,
            String section,
            String photoPath,
            Integer faceLabel) {

        this.id = id;
        this.rollNumber = rollNumber;
        this.name = name;
        this.email = email;
        this.department = department;
        this.year = year;
        this.section = section;
        this.photoPath = photoPath;
        this.faceLabel = faceLabel;
    }

    // ==========================================
    // ID
    // ==========================================

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    // ==========================================
    // ROLL NUMBER
    // ==========================================

    public String getRollNumber() {
        return rollNumber;
    }

    public void setRollNumber(String rollNumber) {
        this.rollNumber = rollNumber;
    }

    // ==========================================
    // NAME
    // ==========================================

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    // ==========================================
    // EMAIL
    // ==========================================

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    // ==========================================
    // DEPARTMENT
    // ==========================================

    public String getDepartment() {
        return department;
    }

    public void setDepartment(String department) {
        this.department = department;
    }

    // ==========================================
    // YEAR
    // ==========================================

    public String getYear() {
        return year;
    }

    public void setYear(String year) {
        this.year = year;
    }

    // ==========================================
    // SECTION
    // ==========================================

    public String getSection() {
        return section;
    }

    public void setSection(String section) {
        this.section = section;
    }

    // ==========================================
    // PHOTO PATH
    // ==========================================

    public String getPhotoPath() {
        return photoPath;
    }

    public void setPhotoPath(String photoPath) {
        this.photoPath = photoPath;
    }

    // ==========================================
    // AI FACE LABEL
    // ==========================================

    public Integer getFaceLabel() {
        return faceLabel;
    }

    public void setFaceLabel(Integer faceLabel) {
        this.faceLabel = faceLabel;
    }
}