import axios from "axios";

const API_URL = "https://multimodal-smart-attendance-system-production.up.railway.app/students";

// GET ALL STUDENTS
export const getStudents = () => {
  return axios.get(API_URL);
};

// ADD STUDENT WITH PHOTO
export const addStudent = async (student, photo) => {
  const formData = new FormData();

  formData.append(
    "student",
    JSON.stringify(student)
  );

  formData.append(
    "photo",
    photo
  );

  return await axios.post(
    API_URL,
    formData
  );
};

// UPDATE STUDENT
export const updateStudent = (id, student) => {
  return axios.put(
    `${API_URL}/${id}`,
    student
  );
};

// DELETE STUDENT
export const deleteStudent = (id) => {
  return axios.delete(
    `${API_URL}/${id}`
  );
};
