import axios from "axios";

const VIDEO_API_URL =
  "https://multimodal-smart-attendance-system-production.up.railway.app/api/videos";

export const uploadVideos = async (entryVideo, exitVideo) => {
  const formData = new FormData();

  formData.append("entryVideo", entryVideo);
  formData.append("exitVideo", exitVideo);

  const response = await axios.post(
    `${VIDEO_API_URL}/upload`,
    formData
  );

  return response;
};

export const getVideoProcessingStatus = async () => {
  const response = await axios.get(
    `${VIDEO_API_URL}/status`
  );

  return response.data;
};