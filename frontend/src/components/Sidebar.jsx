import { NavLink } from "react-router-dom";

import {
  FaHome,
  FaUserPlus,
  FaUsers,
  FaClipboardList,
  FaCog,
  FaSignOutAlt
} from "react-icons/fa";

import "./Sidebar.css";

function Sidebar() {
  return (
    <div className="sidebar">

      <div className="sidebar-top">

        <img
          src="/logo.png"
          alt="Logo"
          className="sidebar-logo"
        />

        <h2>Smart Attendance</h2>

        <p>Faculty Panel</p>

      </div>

      <div className="sidebar-menu">

        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            isActive ? "menu active" : "menu"
          }
        >
          <FaHome />
          <span>Dashboard</span>
        </NavLink>

        <NavLink
          to="/add-student"
          className={({ isActive }) =>
            isActive ? "menu active" : "menu"
          }
        >
          <FaUserPlus />
          <span>Add Student</span>
        </NavLink>

        <NavLink
          to="/students"
          className={({ isActive }) =>
            isActive ? "menu active" : "menu"
          }
        >
          <FaUsers />
          <span>Student List</span>
        </NavLink>

        <NavLink
          to="/attendance"
          className={({ isActive }) =>
            isActive ? "menu active" : "menu"
          }
        >
          <FaClipboardList />
          <span>Daily Records</span>
        </NavLink>

        <NavLink
          to="/settings"
          className={({ isActive }) =>
            isActive ? "menu active" : "menu"
          }
        >
          <FaCog />
          <span>Settings</span>
        </NavLink>

      </div>

      <div className="sidebar-bottom">

        <NavLink
          to="/"
          className="logout"
        >
          <FaSignOutAlt />
          <span>Logout</span>
        </NavLink>

      </div>

    </div>
  );
}

export default Sidebar;