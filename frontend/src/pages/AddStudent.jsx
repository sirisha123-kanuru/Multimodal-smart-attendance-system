import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { addStudent } from "../services/studentService";
import "./AddStudent.css";

function AddStudent() {
  const navigate = useNavigate();

  // Student details
  const [student, setStudent] = useState({
    rollNumber: "",
    name: "",
    email: "",
    department: "",
    year: "",
    section: "",
  });

  // Actual student photo
  const [photo, setPhoto] = useState(null);

  // ============================
  // Handle Input Change
  // ============================
  const handleChange = (e) => {
    const { name, value } = e.target;

    setStudent((previousStudent) => ({
      ...previousStudent,
      [name]: value,
    }));
  };

  // ============================
  // Handle Photo Selection
  // ============================
  const handlePhoto = (e) => {
    const selectedFile = e.target.files?.[0];

    if (selectedFile) {
      setPhoto(selectedFile);
      console.log("Selected photo:", selectedFile);
    }
  };

  // ============================
  // Save Student
  // ============================
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Check student fields
    if (
      student.rollNumber.trim() === "" ||
      student.name.trim() === "" ||
      student.email.trim() === "" ||
      student.department.trim() === "" ||
      student.year === "" ||
      student.section === ""
    ) {
      alert("Please fill all fields.");
      return;
    }

    // Check photo
    if (!photo) {
      alert("Please select a student photo.");
      return;
    }

    try {
      console.log("Student data:", student);
      console.log("Photo:", photo);

      const response = await addStudent(student, photo);

      console.log("Student registration response:", response.data);

      alert("Student Registered Successfully!");

      // Reset form
      setStudent({
        rollNumber: "",
        name: "",
        email: "",
        department: "",
        year: "",
        section: "",
      });

      setPhoto(null);

      navigate("/students");
    } catch (error) {
      console.error("FULL ERROR:", error);
      console.error("STATUS:", error.response?.status);
      console.error("RESPONSE:", error.response);
      console.error("RESPONSE DATA:", error.response?.data);

      if (error.response) {
        alert(
          "Failed to register student.\n\n" +
            "Status: " +
            error.response.status +
            "\n\nCheck Console for details."
        );
      } else if (error.request) {
        alert(
          "Backend is not responding.\n\n" +
            "Make sure Spring Boot is running on port 8081."
        );
      } else {
        alert("Failed to register student: " + error.message);
      }
    }
  };

  return (
    <div className="dashboard">
      <Sidebar />

      <div className="dashboard-content">
        <h1 className="page-title">Student Registration</h1>

        <div className="student-card">
          <form onSubmit={handleSubmit}>
            <div className="form-grid">

              {/* Roll Number */}
              <div className="form-group">
                <label>Roll Number</label>

                <input
                  type="text"
                  name="rollNumber"
                  value={student.rollNumber}
                  onChange={handleChange}
                  placeholder="Enter Roll Number"
                  required
                />
              </div>

              {/* Student Name */}
              <div className="form-group">
                <label>Student Name</label>

                <input
                  type="text"
                  name="name"
                  value={student.name}
                  onChange={handleChange}
                  placeholder="Enter Student Name"
                  required
                />
              </div>

              {/* Email */}
              <div className="form-group">
                <label>Email</label>

                <input
                  type="email"
                  name="email"
                  value={student.email}
                  onChange={handleChange}
                  placeholder="Enter Email"
                  required
                />
              </div>

              {/* Department */}
              <div className="form-group">
                <label>Department</label>

                <input
                  type="text"
                  name="department"
                  value={student.department}
                  onChange={handleChange}
                  placeholder="Enter Department"
                  required
                />
              </div>

              {/* Year */}
              <div className="form-group">
                <label>Year</label>

                <select
                  name="year"
                  value={student.year}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select Year</option>
                  <option value="1st Year">1st Year</option>
                  <option value="2nd Year">2nd Year</option>
                  <option value="3rd Year">3rd Year</option>
                  <option value="4th Year">4th Year</option>
                </select>
              </div>

              {/* Section */}
              <div className="form-group">
                <label>Section</label>

                <select
                  name="section"
                  value={student.section}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select Section</option>
                  <option value="A">A</option>
                  <option value="B">B</option>
                  <option value="C">C</option>
                  <option value="D">D</option>
                </select>
              </div>

              {/* Student Photo */}
              <div className="form-group">
                <label>Student Photo</label>

                <input
                  type="file"
                  accept="image/*"
                  onChange={handlePhoto}
                  required
                />

                {photo && <p>Selected: {photo.name}</p>}
              </div>
            </div>

            <button type="submit" className="save-btn">
              Save Student
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default AddStudent;