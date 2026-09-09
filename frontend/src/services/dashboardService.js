import axios from "axios";

const STUDENT_API = "https://multimodal-smart-attendance-system-production.up.railway.app/students";
const ATTENDANCE_API = "https://multimodal-smart-attendance-system-production.up.railway.app/attendance";

export const getStudents = async () => {
  return await axios.get(STUDENT_API);
};

export const getAttendance = async () => {
  return await axios.get(ATTENDANCE_API);
};
