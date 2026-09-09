import axios from "axios";

const STUDENT_API = "http://localhost:8081/students";
const ATTENDANCE_API = "http://localhost:8081/attendance";

export const getStudents = async () => {
  return await axios.get(STUDENT_API);
};

export const getAttendance = async () => {
  return await axios.get(ATTENDANCE_API);
};
