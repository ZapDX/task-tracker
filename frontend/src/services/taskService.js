import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

export default {
  async getTasks() {
    const response = await apiClient.get("/tasks");
    return response.data;
  },

  async createTask(payload) {
    const response = await apiClient.post("/tasks", payload);
    return response.data;
  },

  async updateTask(id, payload) {
    const response = await apiClient.put(`/tasks/${id}`, payload);
    return response.data;
  },

  async deleteTask(id) {
    await apiClient.delete(`/tasks/${id}`);
  },

  async getTrashedTasks() {
    const response = await apiClient.get("/tasks/trash");
    return response.data;
  },

  async restoreTask(id) {
    const response = await apiClient.post(`/tasks/${id}/restore`);
    return response.data;
  },

  async permanentDeleteTask(id) {
    await apiClient.delete(`/tasks/${id}/permanent`);
  },

  async emptyTrash() {
    await apiClient.delete("/tasks/trash/empty");
  },
};
