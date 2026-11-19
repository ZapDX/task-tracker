import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

export default {
  // Mengambil semua daftar tugas
  async getTasks() {
    const response = await apiClient.get("/tasks");
    return response.data;
  },

  // Membuat tugas baru
  async createTask(payload) {
    const response = await apiClient.post("/tasks", payload);
    return response.data;
  },

  // Memperbarui data tugas (judul, deskripsi, atau status)
  async updateTask(id, payload) {
    const response = await apiClient.put(`/tasks/${id}`, payload);
    return response.data;
  },

  // Menghapus tugas berdasarkan ID
  async deleteTask(id) {
    await apiClient.delete(`/tasks/${id}`);
  },
};
