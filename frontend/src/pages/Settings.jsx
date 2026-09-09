import { useState } from "react";
import Sidebar from "../components/Sidebar";
import "./Settings.css";

function Settings() {

  const [settings, setSettings] = useState({
    facultyName: "Faculty",
    email: "faculty@college.edu",
    department: "CSE-AI",
    recognitionThreshold: 0.70,
    attendanceDuration: 30,
    enableNotifications: true,
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setSettings({
      ...settings,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const handleSave = (e) => {
    e.preventDefault();

    /*
       Phase 2

       React
            ↓
       Spring Boot
            ↓
       MySQL

    */

    alert("Settings Saved Successfully!");
  };

  return (

    <div className="dashboard">

      <Sidebar />

      <div className="dashboard-content">

        <h1 className="page-title">

          Settings

        </h1>

        <div className="settings-card">

          <form onSubmit={handleSave}>

            <div className="form-group">

              <label>Faculty Name</label>

              <input
                type="text"
                name="facultyName"
                value={settings.facultyName}
                onChange={handleChange}
              />

            </div>

            <div className="form-group">

              <label>Email</label>

              <input
                type="email"
                name="email"
                value={settings.email}
                onChange={handleChange}
              />

            </div>

            <div className="form-group">

              <label>Department</label>

              <input
                type="text"
                name="department"
                value={settings.department}
                onChange={handleChange}
              />

            </div>

            <div className="form-group">

              <label>

                Face Recognition Threshold

              </label>

              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                name="recognitionThreshold"
                value={settings.recognitionThreshold}
                onChange={handleChange}
              />

            </div>

            <div className="form-group">

              <label>

                Minimum Attendance Duration (Minutes)

              </label>

              <input
                type="number"
                name="attendanceDuration"
                value={settings.attendanceDuration}
                onChange={handleChange}
              />

            </div>

            <div className="checkbox-group">

              <input
                type="checkbox"
                name="enableNotifications"
                checked={settings.enableNotifications}
                onChange={handleChange}
              />

              <label>

                Enable Email Notifications

              </label>

            </div>

            <button
              className="save-btn"
              type="submit"
            >
              Save Settings
            </button>

          </form>

        </div>

      </div>

    </div>

  );

}

export default Settings;