package com.attendance.controller;

import com.attendance.entity.Attendance;
import com.attendance.service.AttendanceService;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/attendance")
@CrossOrigin(origins = {
        "http://localhost:5173",
        "http://localhost:5174"
})
public class AttendanceController {

    @Autowired
    private AttendanceService attendanceService;


    // ==========================================
    // ADD ATTENDANCE
    // ==========================================

    @PostMapping
    public Attendance addAttendance(
            @RequestBody Attendance attendance
    ) {
        return attendanceService.addAttendance(attendance);
    }


    // ==========================================
    // GET ALL ATTENDANCE
    // ==========================================

    @GetMapping
    public List<Attendance> getAllAttendance() {
        return attendanceService.getAllAttendance();
    }


    // ==========================================
    // GET ATTENDANCE BY ID
    // ==========================================

    @GetMapping("/{id}")
    public Attendance getAttendanceById(
            @PathVariable Long id
    ) {
        return attendanceService.getAttendanceById(id);
    }


    // ==========================================
    // GET ATTENDANCE BY DATE
    // ==========================================

    @GetMapping("/date/{date}")
    public List<Attendance> getAttendanceByDate(
            @PathVariable LocalDate date
    ) {
        return attendanceService.getAttendanceByDate(date);
    }


    // ==========================================
    // GET ATTENDANCE BY STUDENT ID
    // ==========================================

    @GetMapping("/student/{studentId}")
    public List<Attendance> getAttendanceByStudentId(
            @PathVariable Long studentId
    ) {
        return attendanceService
                .getAttendanceByStudentId(studentId);
    }


    // ==========================================
    // UPDATE ATTENDANCE
    // ==========================================

    @PutMapping("/{id}")
    public Attendance updateAttendance(
            @PathVariable Long id,
            @RequestBody Attendance attendance
    ) {

        attendance.setId(id);

        return attendanceService
                .updateAttendance(attendance);
    }


    // ==========================================
    // DELETE ATTENDANCE
    // ==========================================

    @DeleteMapping("/{id}")
    public String deleteAttendance(
            @PathVariable Long id
    ) {

        attendanceService.deleteAttendance(id);

        return "Attendance Deleted Successfully";
    }
}