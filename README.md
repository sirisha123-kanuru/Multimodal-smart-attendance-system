# Multimodal Smart Attendance System

An AI-based smart attendance system that combines **face recognition, entry/exit video processing, timestamp analysis, duration validation, and database management** to automatically determine student attendance.

---

## 📌 Project Overview

The **Multimodal Smart Attendance System** is designed to automate the attendance process using facial recognition technology.

The system identifies registered students from entry and exit videos, records their entry and exit timestamps, calculates their attendance duration, and automatically determines whether they are **PRESENT** or **ABSENT** based on a minimum required duration.

Unlike a basic face-detection attendance system, this project considers multiple types of information:

- Student registration data
- Facial information
- Entry video
- Exit video
- Entry and exit timestamps
- Attendance duration
- Attendance rules
- Database records

---

## 🎯 Objectives

- Automate student attendance using face recognition.
- Register students with their personal and facial information.
- Assign a unique face label to each student.
- Detect and recognize students from video.
- Record entry and exit timestamps automatically.
- Calculate the duration of student presence.
- Apply attendance validation rules.
- Store attendance information in MySQL.
- Provide an interactive React dashboard.
- Identify students who are absent from both entry and exit videos.

---

## ✨ Features

### Student Registration

- Student name and roll number registration.
- Student photo upload.
- Automatic unique face label assignment.
- Student information stored in MySQL.

### Face Recognition

- OpenCV-based face detection.
- Haar Cascade for face detection.
- Face recognition model for identifying registered students.
- Recognition based on assigned face labels.

### Entry Video Processing

- Processes an uploaded entry video.
- Detects registered students.
- Records video-relative entry timestamps.
- Updates attendance records.

### Exit Video Processing

- Processes an uploaded exit video.
- Detects students leaving the classroom.
- Records video-relative exit timestamps.
- Updates existing attendance records.

### Duration Validation

The system checks the duration between entry and exit.

Minimum required duration:

**45 minutes**

Attendance rule:

```text
Entry NO + Exit NO
        ↓
      ABSENT

Entry YES + Exit NO
        ↓
 Apply duration rule

Entry YES + Exit YES
        ↓
 Calculate duration

Duration >= 45 minutes
        ↓
      PRESENT

Duration < 45 minutes
        ↓
      ABSENT
