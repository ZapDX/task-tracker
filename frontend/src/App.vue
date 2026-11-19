<script setup>
import { computed, onMounted, ref } from "vue";
import TaskForm from "./components/TaskForm.vue";
import TaskItem from "./components/TaskItem.vue";
import taskService from "./services/taskService";

const tasks = ref([]);
const isLoading = ref(true);
const errorMessage = ref("");
const activeFilter = ref("All");

const filterOptions = ["All", "Todo", "In Progress", "Done"];

const fetchTasks = async () => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    tasks.value = await taskService.getTasks();
  } catch (error) {
    errorMessage.value = "Gagal memuat daftar tugas. Pastikan server backend FastAPI sudah berjalan.";
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};

const handleAddTask = async (payload) => {
  errorMessage.value = "";
  try {
    const createdTask = await taskService.createTask(payload);
    // Langsung tambahkan ke urutan paling atas state tanpa reload halaman
    tasks.value.unshift(createdTask);
  } catch (error) {
    errorMessage.value = error.response?.data?.detail?.[0]?.msg || "Gagal menambahkan tugas baru.";
    throw error;
  }
};

const handleUpdateTask = async (id, payload) => {
  errorMessage.value = "";
  try {
    const updatedTask = await taskService.updateTask(id, payload);
    const index = tasks.value.findIndex((t) => t.id === id);
    if (index !== -1) {
      tasks.value[index] = updatedTask;
    }
  } catch (error) {
    errorMessage.value = "Gagal memperbarui tugas.";
    console.error(error);
  }
};

const handleDeleteTask = async (id) => {
  errorMessage.value = "";
  try {
    await taskService.deleteTask(id);
    tasks.value = tasks.value.filter((t) => t.id !== id);
  } catch (error) {
    errorMessage.value = "Gagal menghapus tugas.";
    console.error(error);
  }
};

const filteredTasks = computed(() => {
  if (activeFilter.value === "All") return tasks.value;
  return tasks.value.filter((task) => task.status === activeFilter.value);
});

const taskCounts = computed(() => ({
  All: tasks.value.length,
  Todo: tasks.value.filter((t) => t.status === "Todo").length,
  "In Progress": tasks.value.filter((t) => t.status === "In Progress").length,
  Done: tasks.value.filter((t) => t.status === "Done").length,
}));

onMounted(() => {
  fetchTasks();
});
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 py-8 px-4 sm:px-6">
    <div class="max-w-3xl mx-auto">
      <!-- Header -->
      <header class="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-slate-900">Simple Task Tracker</h1>
          <p class="text-sm text-slate-500">Catat, pantau progres, dan kelola daftar tugas harianmu.</p>
        </div>
        <span class="inline-flex items-center self-start sm:self-center rounded-full bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700 border border-indigo-100"> Total: {{ taskCounts.All }} Tugas </span>
      </header>

      <!-- Banner Error -->
      <div v-if="errorMessage" class="mb-5 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 flex items-center justify-between">
        <span>{{ errorMessage }}</span>
        <button @click="fetchTasks" class="ml-4 text-xs font-semibold underline hover:text-rose-900 cursor-pointer">Coba Lagi</button>
      </div>

      <!-- Form Input Tugas -->
      <TaskForm @add-task="handleAddTask" />

      <!-- Filter Tabs -->
      <div class="flex items-center gap-2 overflow-x-auto pb-2 mb-4">
        <button
          v-for="filter in filterOptions"
          :key="filter"
          @click="activeFilter = filter"
          class="px-3.5 py-1.5 rounded-lg text-xs font-medium transition cursor-pointer whitespace-nowrap"
          :class="activeFilter === filter ? 'bg-slate-900 text-white shadow-sm' : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'"
        >
          {{ filter }} ({{ taskCounts[filter] }})
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-12 text-sm text-slate-500">Memuat daftar tugas...</div>

      <!-- Empty State -->
      <div v-else-if="filteredTasks.length === 0" class="bg-white rounded-xl border border-dashed border-slate-300 p-10 text-center">
        <p class="text-sm font-medium text-slate-600 mb-1">Belum ada tugas pada kategori "{{ activeFilter }}"</p>
        <p class="text-xs text-slate-400">Tambahkan tugas baru melalui form di atas untuk memulai.</p>
      </div>

      <!-- Task List -->
      <div v-else class="space-y-3">
        <TaskItem v-for="task in filteredTasks" :key="task.id" :task="task" @update-task="handleUpdateTask" @delete-task="handleDeleteTask" />
      </div>
    </div>
  </div>
</template>
