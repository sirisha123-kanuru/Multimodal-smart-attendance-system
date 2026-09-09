import axios from "axios";

const API_URL = "http://localhost:8081/attendance";

export const getAttendance = () => axios.get(API_URL);

export const getAttendanceById = (id) =>
  axios.get(`${API_URL}/${id}`);

export const getAttendanceByDate = (date) =>
  axios.get(`${API_URL}/date/${date}`);

export const getAttendanceByStudent = (studentId) =>
  axios.get(`${API_URL}/student/${studentId}`);

export const addAttendance = (attendance) =>
  axios.post(API_URL, attendance);

export const updateAttendance = (id, attendance) =>
  axios.put(`${API_URL}/${id}`, attendance);

export const deleteAttendance = (id) =>
  axios.delete(`${API_URL}/${id}`);