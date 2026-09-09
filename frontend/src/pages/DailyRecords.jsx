import { useState } from "react";
import Sidebar from "../components/Sidebar";
import { getAttendanceByDate } from "../services/attendanceService";
import "./DailyRecords.css";

function DailyRecords() {

  const [selectedDate, setSelectedDate] = useState("");
  const [records, setRecords] = useState([]);

  const handleSearch = async () => {

    if (selectedDate === "") {
      alert("Please select a date.");
      return;
    }

    try {

      const response = await getAttendanceByDate(selectedDate);

      console.log(response.data);

      setRecords(response.data);

    } catch (error) {

      console.error(error);

      alert("No attendance found.");

      setRecords([]);

    }
  };

  return (

    <div className="dashboard">

      <Sidebar />

      <div className="dashboard-content">

        <h1 className="page-title">
          Daily Attendance Records
        </h1>

        {/* Search */}

        <div className="search-card">

          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
          />

          <button
            className="search-btn"
            onClick={handleSearch}
          >
            Search
          </button>

        </div>

        {/* Table */}

        <div className="table-card">

          <table>

            <thead>

              <tr>

                <th>ID</th>
                <th>Student ID</th>
                <th>Date</th>
                <th>Entry Time</th>
                <th>Exit Time</th>
                <th>Status</th>

              </tr>

            </thead>

            <tbody>

              {

                records.length === 0 ?

                  (

                    <tr>

                      <td
                        colSpan="6"
                        className="empty-row"
                      >

                        No Attendance Found

                      </td>

                    </tr>

                  )

                  :

                  (

                    records.map((record) => (

                      <tr key={record.id}>

                        <td>{record.id}</td>

                        <td>{record.studentId}</td>

                        <td>{record.date}</td>

                        <td>{record.entryTime}</td>

                        <td>{record.exitTime}</td>

                        <td>

                          <span
                            className={
                              record.status === "Present"
                                ? "present"
                                : "absent"
                            }
                          >

                            {record.status}

                          </span>

                        </td>

                      </tr>

                    ))

                  )

              }

            </tbody>

          </table>

        </div>

      </div>

    </div>

  );

}

export default DailyRecords;