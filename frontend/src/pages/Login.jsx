import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaUser, FaLock, FaCamera } from "react-icons/fa";
import "./Login.css";

function Login() {

  const navigate = useNavigate();

  const [facultyId, setFacultyId] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = () => {

  console.log("Login button clicked");
  console.log("Faculty ID:", facultyId);
  console.log("Password:", password);

  if (
    facultyId.trim() === "FAC001" &&
    password.trim() === "admin123"
  ) {

    console.log("Login Success");
    navigate("/dashboard");

  } else {

    console.log("Login Failed");
    alert("Invalid Faculty ID or Password");

  }

};

  return (

    <div className="login-container">

      {/* Left Panel */}

      <div className="login-left">

        <img
          src="/logo.png"
          alt="Logo"
          className="logo"
        />

        <h1>

          Smart Attendance System

        </h1>

        <p>

          AI Powered Face Recognition
          Attendance System

        </p>

        <img
          src="/faculty.png"
          alt="Faculty"
          className="faculty-image"
        />

      </div>

      {/* Right Panel */}

      <div className="login-right">

        <div className="login-card">

          <h2>

            Faculty Login

          </h2>

          <p className="subtitle">

            Welcome Back

          </p>

          {/* Faculty ID */}

          <div className="input-box">

            <FaUser className="input-icon" />

            <input

              type="text"

              placeholder="Faculty ID"

              value={facultyId}

              onChange={(e)=>
                setFacultyId(
                  e.target.value
                )
              }

            />

          </div>

          {/* Password */}

          <div className="input-box">

            <FaLock className="input-icon" />

            <input

              type="password"

              placeholder="Password"

              value={password}

              onChange={(e)=>
                setPassword(
                  e.target.value
                )
              }

            />

          </div>

          {/* Face Verification */}

          <div className="camera-box">

            <FaCamera
              className="camera-icon"
            />

            <h3>

              Face Verification

            </h3>

            <p>

              Camera verification
              will be enabled
              in Phase 3

            </p>

            <button
              type="button"
              className="camera-btn"
            >

              Start Camera

            </button>

          </div>

          {/* Login */}

          <button

            className="login-btn"

            onClick={handleLogin}

          >

            Login

          </button>

          {/* Demo */}

          <div className="demo-box">

            <h4>

              Demo Credentials

            </h4>

            <p>

              Faculty ID :
              <strong> FAC001</strong>

            </p>

            <p>

              Password :
              <strong> admin123</strong>

            </p>

          </div>

        </div>

      </div>

    </div>

  );

}

export default Login;