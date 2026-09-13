import { useState, useEffect } from "react";

import {
  FaUsers,
  FaUserCheck,
  FaUserTimes,
  FaRobot,
} from "react-icons/fa";

import Sidebar from "../components/Sidebar";
import StatCard from "../components/StatCard";
import UploadCard from "../components/UploadCard";

import { getStudents } from "../services/dashboardService";
import { getAttendance } from "../services/attendanceService";
import {
  uploadVideos,
  getVideoProcessingStatus
} from "../services/videoService";

import "./Dashboard.css";

function Dashboard() {

  // ============================================================
  // VIDEO STATES
  // ============================================================

  const [entryVideo, setEntryVideo] = useState(null);
  const [exitVideo, setExitVideo] = useState(null);


  // ============================================================
  // PROCESSING STATES
  // ============================================================

  const [status, setStatus] = useState(
    "Waiting for Videos..."
  );

  const [attendance, setAttendance] = useState([]);

  const [isProcessing, setIsProcessing] = useState(false);


  // ============================================================
  // DASHBOARD STATISTICS
  // ============================================================

  const [totalStudents, setTotalStudents] = useState(0);
  const [presentStudents, setPresentStudents] = useState(0);
  const [absentStudents, setAbsentStudents] = useState(0);


  // ============================================================
  // INITIAL DASHBOARD LOAD
  //
  // IMPORTANT:
  // Only load registered students here.
  //
  // DO NOT load old attendance when Dashboard opens.
  // Present and Absent must remain 0 until the user
  // processes new Entry + Exit videos.
  // ============================================================

  useEffect(() => {
    loadStudentsOnly();
  }, []);


  // ============================================================
  // LOAD REGISTERED STUDENTS ONLY
  // ============================================================

  const loadStudentsOnly = async () => {

    try {

      const response = await getStudents();

      const students = Array.isArray(response.data)
        ? response.data
        : [];


      // Total registered students
      setTotalStudents(students.length);


      // IMPORTANT:
      // No video processed yet in this Dashboard session.
      setPresentStudents(0);
      setAbsentStudents(0);

      setAttendance([]);

      setStatus("Waiting for Videos...");


    } catch (error) {

      console.error(
        "Student Loading Error:",
        error
      );

      setTotalStudents(0);
      setPresentStudents(0);
      setAbsentStudents(0);
      setAttendance([]);

    }

  };


  // ============================================================
  // LOAD ATTENDANCE AFTER VIDEO PROCESSING
  // ============================================================

  const loadProcessedAttendance = async () => {

    try {

      // --------------------------------------------------------
      // GET REGISTERED STUDENTS
      // --------------------------------------------------------

      const studentResponse =
        await getStudents();

      const students = Array.isArray(
        studentResponse.data
      )
        ? studentResponse.data
        : [];


      // Update total
      setTotalStudents(
        students.length
      );


      // --------------------------------------------------------
      // GET ATTENDANCE
      // --------------------------------------------------------

      const attendanceResponse =
        await getAttendance();

      let records = Array.isArray(
        attendanceResponse.data
      )
        ? attendanceResponse.data
        : [];


      console.log(
        "All Attendance Records:",
        records
      );


      // --------------------------------------------------------
      // NO ATTENDANCE RECORDS
      // --------------------------------------------------------

      if (records.length === 0) {

        const absentRecords =
          students.map(
            (student) => ({
              id:
                `absent-${student.id}`,

              studentId:
                student.id,

              rollNumber:
                student.rollNumber,

              name:
                student.name,

              entryTime:
                null,

              exitTime:
                null,

              status:
                "ABSENT",

              date:
                null,
            })
          );


        setAttendance(
          absentRecords
        );

        setPresentStudents(0);

        setAbsentStudents(
          students.length
        );

        return absentRecords;

      }


      // ========================================================
      // FIND LATEST ATTENDANCE DATE
      // ========================================================

      const availableDates =
        records
          .map(
            (record) =>
              record.date
          )
          .filter(Boolean);


      if (
        availableDates.length === 0
      ) {

        setAttendance([]);

        setPresentStudents(0);

        setAbsentStudents(
          students.length
        );

        return [];

      }


      const latestDate =
        availableDates.reduce(
          (latest, current) =>
            current > latest
              ? current
              : latest
        );


      console.log(
        "Latest Attendance Date:",
        latestDate
      );


      // ========================================================
      // ONLY LATEST DATE
      // ========================================================

      records =
        records.filter(
          (record) =>
            record.date ===
            latestDate
        );


      console.log(
        "Latest Attendance Records:",
        records
      );


      // ========================================================
      // CREATE FINAL ATTENDANCE
      //
      // IMPORTANT:
      // Start with ALL registered students.
      //
      // This guarantees that a student who is NOT found
      // in the videos will still appear as ABSENT.
      // ========================================================

      const finalAttendance =
        students.map(
          (student) => {

            // --------------------------------------------------
            // Find attendance record
            // --------------------------------------------------

            const studentRecords =
              records.filter(
                (record) =>
                  String(
                    record.studentId
                  ) ===
                  String(
                    student.id
                  )
              );


            // --------------------------------------------------
            // Latest record for this student
            // --------------------------------------------------

            let record = null;


            if (
              studentRecords.length > 0
            ) {

              record =
                studentRecords.reduce(
                  (
                    latest,
                    current
                  ) => {

                    if (!latest) {
                      return current;
                    }


                    return Number(
                      current.id
                    ) >
                    Number(
                      latest.id
                    )
                      ? current
                      : latest;

                  },
                  null
                );

            }


            // ==================================================
            // STUDENT NOT FOUND IN VIDEO
            // ==================================================

            if (!record) {

              return {

                id:
                  `absent-${student.id}`,

                studentId:
                  student.id,

                rollNumber:
                  student.rollNumber,

                name:
                  student.name,

                entryTime:
                  null,

                exitTime:
                  null,

                status:
                  "ABSENT",

                date:
                  latestDate,

              };

            }


            // ==================================================
            // STUDENT FOUND IN ATTENDANCE
            // ==================================================

            return {

              id:
                record.id,

              studentId:
                student.id,

              rollNumber:
                student.rollNumber,

              name:
                student.name,

              entryTime:
                record.entryTime,

              exitTime:
                record.exitTime,

              status:
                String(
                  record.status || ""
                ).toUpperCase(),

              date:
                record.date,

            };

          }
        );


      // ========================================================
      // SAVE FINAL RESULT
      // ========================================================

      setAttendance(
        finalAttendance
      );


      // ========================================================
      // PRESENT COUNT
      // ========================================================

      const presentCount =
        finalAttendance.filter(
          (student) =>
            String(
              student.status
            ).toUpperCase() ===
            "PRESENT"
        ).length;


      // ========================================================
      // ABSENT COUNT
      // ========================================================

      const absentCount =
        finalAttendance.filter(
          (student) =>
            String(
              student.status
            ).toUpperCase() ===
            "ABSENT"
        ).length;


      setPresentStudents(
        presentCount
      );

      setAbsentStudents(
        absentCount
      );


      console.log(
        "FINAL ATTENDANCE:",
        finalAttendance
      );


      return finalAttendance;


    } catch (error) {

      console.error(
        "Attendance Loading Error:",
        error
      );

      setAttendance([]);

      setPresentStudents(0);
      setAbsentStudents(0);

      throw error;

    }

  };


  // ============================================================
  // PROCESS ATTENDANCE
  // ============================================================

  const handleProcess = async () => {

    // ----------------------------------------------------------
    // BOTH VIDEOS REQUIRED
    // ----------------------------------------------------------

    if (!entryVideo || !exitVideo) {
      alert("Please upload both Entry and Exit videos.");
      return;
    }

    try {
      setIsProcessing(true);

      setStatus("Uploading Entry and Exit Videos...");

      const response = await uploadVideos(
        entryVideo,
        exitVideo
      );

      console.log(
        "Video Upload Response:",
        response.data
      );

      setStatus(
        "Videos uploaded. AI processing started..."
      );

      console.log(
        "Waiting for background AI processing..."
      );

      let processingCompleted = false;
      const maxAttempts = 120;

      for (let attempt = 1; attempt <= maxAttempts; attempt++) {

        await new Promise(
          (resolve) => setTimeout(resolve, 5000)
        );

        const processingStatus =
          await getVideoProcessingStatus();

        console.log(
          `AI Processing Status (${attempt}/${maxAttempts}):`,
          processingStatus
        );

        if (processingStatus.status === "COMPLETED") {
          processingCompleted = true;

          setStatus(
            "AI processing completed. Loading attendance..."
          );

          break;
        }

        if (processingStatus.status === "FAILED") {
          throw new Error(
            processingStatus.error ||
            "AI video processing failed."
          );
        }

        setStatus(
          `AI Processing... Please wait (${attempt}/${maxAttempts})`
        );
      }

      if (!processingCompleted) {
        throw new Error(
          "AI processing is taking too long. Please check Railway logs."
        );
      }

      await loadProcessedAttendance();

      setStatus(
        "AI Attendance Processing Completed."
      );

      alert(
        "Entry and Exit videos processed successfully."
      );

    } catch (error) {

      console.error(
        "Video Processing Error:",
        error
      );

      setStatus(
        "Video Processing Failed."
      );

      if (error.response) {

        console.error(
          "Backend Response:",
          error.response.data
        );

        alert(
          typeof error.response.data === "string"
            ? error.response.data
            : "Video processing failed. Please check the backend."
        );

      } else if (error.request) {

        alert(
          "Cannot connect to Spring Boot backend. " +
          "Please check the Railway backend."
        );

      } else {

        alert(
          error.message ||
          "Something went wrong while processing videos."
        );
      }

    } finally {
      setIsProcessing(false);
    }

  };

  // ============================================================
  // UI
  // ============================================================

  return (

    <div className="dashboard-layout">

      {/* ======================================================
          SIDEBAR
      ====================================================== */}

      <Sidebar />


      {/* ======================================================
          MAIN CONTENT
      ====================================================== */}

      <div className="dashboard-content">


        {/* ====================================================
            HEADER
        ==================================================== */}

        <div className="dashboard-header">

          <div>

            <h1>
              Dashboard
            </h1>

            <p>
              AI Based Smart Attendance System
            </p>

          </div>

        </div>


        {/* ====================================================
            STATISTICS
        ==================================================== */}

        <div className="stats-grid">

          <StatCard
            title="Total Students"
            value={totalStudents}
            icon={<FaUsers />}
            color="#2563eb"
          />


          <StatCard
            title="Present"
            value={presentStudents}
            icon={<FaUserCheck />}
            color="#16a34a"
          />


          <StatCard
            title="Absent"
            value={absentStudents}
            icon={<FaUserTimes />}
            color="#dc2626"
          />


          <StatCard
            title="System Status"
            value={
              isProcessing
                ? "Processing"
                : "Ready"
            }
            icon={<FaRobot />}
            color="#7c3aed"
          />

        </div>


        {/* ====================================================
            VIDEO UPLOAD
        ==================================================== */}

        <div className="upload-grid">

          <UploadCard
            title="Upload Entry Video"
            accept="video/*"
            onFileSelect={
              setEntryVideo
            }
          />


          <UploadCard
            title="Upload Exit Video"
            accept="video/*"
            onFileSelect={
              setExitVideo
            }
          />

        </div>


        {/* ====================================================
            AI PROCESSING
        ==================================================== */}

        <div className="process-card">

          <h2>
            AI Attendance Processing
          </h2>


          <p>

            <strong>
              Status :
            </strong>{" "}

            {status}

          </p>


          <button
            className="process-btn"
            onClick={handleProcess}
            disabled={isProcessing}
          >

            {isProcessing
              ? "Processing Attendance..."
              : "Process Attendance"}

          </button>

        </div>


        {/* ====================================================
            ATTENDANCE RECORDS
        ==================================================== */}

        <div className="attendance-card">

          <h2>
            Attendance Records
          </h2>


          {attendance.length === 0 ? (

            <div className="empty-box">

              <h3>
                No Attendance Processed Yet
              </h3>

              <p>
                Upload Entry and Exit videos
                and click Process Attendance
                to generate attendance.
              </p>

            </div>

          ) : (

            <table>

              <thead>

                <tr>

                  <th>
                    Roll No
                  </th>

                  <th>
                    Name
                  </th>

                  <th>
                    Entry Time
                  </th>

                  <th>
                    Exit Time
                  </th>

                  <th>
                    Status
                  </th>

                </tr>

              </thead>


              <tbody>

                {attendance.map(
                  (student) => (

                    <tr
                      key={
                        student.id
                      }
                    >

                      <td>
                        {
                          student.rollNumber ||
                          "-"
                        }
                      </td>


                      <td>
                        {
                          student.name ||
                          "-"
                        }
                      </td>


                      <td>
                        {
                          student.entryTime ||
                          "-"
                        }
                      </td>


                      <td>
                        {
                          student.exitTime ||
                          "-"
                        }
                      </td>


                      <td>
                        {
                          student.status ||
                          "-"
                        }
                      </td>

                    </tr>

                  )
                )}

              </tbody>

            </table>

          )}

        </div>

      </div>

    </div>

  );

}
export default Dashboard;