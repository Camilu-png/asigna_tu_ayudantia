import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://localhost:8000/api/v1", // TODO: CREATE A VARIABLE FOR THIS
});

export default apiClient;
