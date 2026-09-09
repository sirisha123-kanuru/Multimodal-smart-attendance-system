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

🛠️ Technology Stack
Frontend -
React.js
JavaScript
CSS
Axios
Vite

Backend -
Java
Spring Boot
Spring REST
Spring Data JPA
Hibernate
Maven

Database -
MySQL

AI / Computer Vision -
Python
OpenCV
Haar Cascade
Face Recognition

Development Environment -
Windows
Visual Studio Code / IntelliJ IDEA
MySQL
Git
GitHub

📂 Project Structure

multimodal-smart-attendance-system/
│
├── ai/
│   ├── capture_faces.py
│   ├── face_detection.py
│   ├── final_attendance.py
│   ├── process_entry_video.py
│   ├── process_exit_video.py
│   ├── recognize_faces.py
│   ├── train_faces.py
│   ├── duration_validation.py
│   └── haarcascade_frontalface_default.xml
│
├── backend/
│   ├── src/
│   ├── pom.xml
│   └── mvnw.cmd
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
└── .gitignore


▶️ How to Run the Project
1. Start MySQL

Make sure MySQL is running and the project database is configured in the Spring Boot application.

2. Start Spring Boot Backend

Open CMD:

cd C:\Users\Sirisha\Desktop\multimodal-smart-attendance-system\backend
mvnw.cmd spring-boot:run

Backend runs on:

http://localhost:8081
3. Start React Frontend

Open another CMD:

cd C:\Users\Sirisha\Desktop\multimodal-smart-attendance-system\frontend
npm install
npm run dev

The frontend will normally run on:

http://localhost:5173
4. Start Python AI Environment

Open CMD:

cd C:\Users\Sirisha\Desktop\multimodal-smart-attendance-system\ai
venv\Scripts\activate
5. Process Entry Video
python process_entry_video.py "entry_video_2.mp4"
6. Process Exit Video
python process_exit_video.py "exit_video.mp4"
7. Run Duration Validation
python duration_validation.py
📊 Attendance Logic

The system compares all registered students with the students detected in the videos.

Case 1: Student not detected in either video
Entry = NO
Exit  = NO

Result = ABSENT
Case 2: Student detected at entry but not at exit
Entry = YES
Exit  = NO

Apply duration validation
Case 3: Student detected at both entry and exit
Entry = YES
Exit  = YES

Calculate duration
Final validation
Duration >= 45 minutes → PRESENT

Duration < 45 minutes → ABSENT


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

