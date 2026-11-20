<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import ConfirmModal from "./components/ConfirmModal.vue";
import KanbanBoard from "./components/KanbanBoard.vue";
import SidebarNav from "./components/SidebarNav.vue";
import TaskForm from "./components/TaskForm.vue";
import TaskItem from "./components/TaskItem.vue";
import ToastNotification from "./components/ToastNotification.vue";
import TrashView from "./components/TrashView.vue";
import taskService from "./services/taskService.js";

const tasks = ref([]);
const trashedTasks = ref([]);
const isLoading = ref(true);
const isLoadingTrash = ref(false);
const errorMessage = ref("");

// Navigasi & Mode Tampilan
const activePage = ref("tasks"); // 'tasks' | 'trash'
const viewMode = ref("list"); // 'list' | 'board'
const isSidebarOpenMobile = ref(false);
const isSidebarOpenDesktop = ref(true);

// Filter, Search & Sort states
const activeFilter = ref("All");
const searchQuery = ref("");
const sortBy = ref("newest");
const filterOptions = ["All", "Todo", "In Progress", "Done"];

// Modal & Toast states
const modalState = ref({
  isOpen: false,
  type: null,
  task: null,
  title: "",
  message: "",
  confirmText: "",
});
const isProcessingModal = ref(false);
const toast = ref(null);
let toastTimeout = null;

const showToast = (message, type = "success") => {
  toast.value = { message, type };
  if (toastTimeout) clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => {
    toast.value = null;
  }, 3000);
};

const fetchAllData = async () => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const [activeList, trashList] = await Promise.all([taskService.getTasks(), taskService.getTrashedTasks()]);
    tasks.value = activeList;
    trashedTasks.value = trashList;
  } catch (error) {
    errorMessage.value = "Gagal memuat daftar tugas. Pastikan server backend FastAPI sudah berjalan.";
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};

const refreshTrash = async () => {
  isLoadingTrash.value = true;
  try {
    trashedTasks.value = await taskService.getTrashedTasks();
  } catch (error) {
    console.error(error);
  } finally {
    isLoadingTrash.value = false;
  }
};

const handleSwitchViewMode = (mode) => {
  viewMode.value = mode;
  if (mode === "board") {
    activeFilter.value = "All";
  }
};

const handleAddTask = async (payload) => {
  errorMessage.value = "";
  try {
    const createdTask = await taskService.createTask(payload);
    tasks.value.unshift(createdTask);
    showToast("Tugas baru berhasil ditambahkan");
  } catch (error) {
    const msg = error.response?.data?.detail?.[0]?.msg || "Gagal menambahkan tugas baru.";
    showToast(msg, "error");
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
    showToast(payload.status === "Done" ? "Tugas ditandai selesai" : "Tugas berhasil diperbarui");
  } catch (error) {
    showToast("Gagal memperbarui tugas", "error");
    console.error(error);
  }
};

// Konfirmasi Modal Handlers
const openSoftDeleteModal = (task) => {
  modalState.value = {
    isOpen: true,
    type: "soft_delete",
    task,
    title: "Pindahkan ke Tong Sampah?",
    message: `Tugas '${task.title}' akan dipindahkan ke tong sampah dan otomatis dihapus permanen setelah 30 hari.`,
    confirmText: "Pindahkan ke Tong Sampah",
  };
};

const openPermanentDeleteModal = (task) => {
  modalState.value = {
    isOpen: true,
    type: "permanent_delete",
    task,
    title: "Hapus Permanen Tugas?",
    message: `Tugas '${task.title}' akan dihapus selamanya dari database dan tidak dapat dipulihkan kembali.`,
    confirmText: "Hapus Permanen",
  };
};

const openEmptyTrashModal = () => {
  modalState.value = {
    isOpen: true,
    type: "empty_trash",
    task: null,
    title: "Kosongkan Seluruh Tong Sampah?",
    message: `Semua (${trashedTasks.value.length}) tugas di dalam tong sampah akan dihapus secara permanen dan tidak bisa dikembalikan.`,
    confirmText: "Kosongkan Sekarang",
  };
};

const closeModal = () => {
  if (isProcessingModal.value) return;
  modalState.value.isOpen = false;
};

const handleConfirmModal = async () => {
  const { type, task } = modalState.value;
  isProcessingModal.value = true;

  try {
    if (type === "soft_delete" && task) {
      await taskService.deleteTask(task.id);
      tasks.value = tasks.value.filter((t) => t.id !== task.id);
      await refreshTrash();
      showToast("Tugas dipindahkan ke tong sampah");
    } else if (type === "permanent_delete" && task) {
      await taskService.permanentDeleteTask(task.id);
      trashedTasks.value = trashedTasks.value.filter((t) => t.id !== task.id);
      showToast("Tugas dihapus secara permanen");
    } else if (type === "empty_trash") {
      await taskService.emptyTrash();
      trashedTasks.value = [];
      showToast("Tong sampah berhasil dikosongkan");
    }
    modalState.value.isOpen = false;
  } catch (error) {
    showToast("Terjadi kesalahan saat memproses permintaan", "error");
    console.error(error);
  } finally {
    isProcessingModal.value = false;
  }
};

const handleRestoreTask = async (id) => {
  try {
    const restored = await taskService.restoreTask(id);
    trashedTasks.value = trashedTasks.value.filter((t) => t.id !== id);
    tasks.value.unshift(restored);
    showToast("Tugas berhasil dipulihkan ke daftar aktif");
  } catch (error) {
    showToast("Gagal memulihkan tugas", "error");
    console.error(error);
  }
};

const displayedTasks = computed(() => {
  let result = [...tasks.value];

  if (viewMode.value === "list" && activeFilter.value !== "All") {
    result = result.filter((task) => task.status === activeFilter.value);
  }

  const keyword = searchQuery.value.trim().toLowerCase();
  if (keyword) {
    result = result.filter((task) => task.title.toLowerCase().includes(keyword) || (task.description && task.description.toLowerCase().includes(keyword)));
  }

  result.sort((a, b) => {
    if (sortBy.value === "oldest") {
      return new Date(a.created_at) - new Date(b.created_at);
    }
    if (sortBy.value === "completed") {
      const aDone = a.completed_at ? new Date(a.completed_at).getTime() : 0;
      const bDone = b.completed_at ? new Date(b.completed_at).getTime() : 0;
      if (bDone !== aDone) return bDone - aDone;
    }
    return new Date(b.created_at) - new Date(a.created_at);
  });

  return result;
});

const taskCounts = computed(() => ({
  All: tasks.value.length,
  Todo: tasks.value.filter((t) => t.status === "Todo").length,
  "In Progress": tasks.value.filter((t) => t.status === "In Progress").length,
  Done: tasks.value.filter((t) => t.status === "Done").length,
}));

const handleKeydown = (e) => {
  if (e.key === "Escape") {
    closeModal();
    isSidebarOpenMobile.value = false;
  }
};

onMounted(() => {
  fetchAllData();
  window.addEventListener("keydown", handleKeydown);
});

onUnmounted(() => {
  window.removeEventListener("keydown", handleKeydown);
});
</script>

<template>
  <div class="min-h-screen flex items-start bg-muted/50 text-foreground">
    <!-- Workspace Sidebar -->
    <SidebarNav
      :active-page="activePage"
      :active-filter="activeFilter"
      :task-counts="taskCounts"
      :trash-count="trashedTasks.length"
      :is-open-mobile="isSidebarOpenMobile"
      :is-open-desktop="isSidebarOpenDesktop"
      @navigate="activePage = $event"
      @select-filter="activeFilter = $event"
      @close-mobile="isSidebarOpenMobile = false"
      @toggle-desktop="isSidebarOpenDesktop = !isSidebarOpenDesktop"
    />

    <!-- Area Konten Utama -->
    <div class="flex-1 min-w-0 flex flex-col">
      <!-- Top Bar (Mobile & Desktop Sidebar Toggle) -->
      <div class="sticky top-0 z-10 flex items-center justify-between border-b border-border bg-card/95 backdrop-blur-xs px-4 sm:px-8 py-3">
        <div class="flex items-center gap-3">
          <!-- Tombol Buka Sidebar Mobile -->
          <button
            @click="isSidebarOpenMobile = true"
            type="button"
            class="inline-flex lg:hidden items-center gap-1.5 rounded-md border border-border bg-background px-2.5 py-1.5 text-xs font-medium text-foreground hover:bg-muted cursor-pointer"
          >
            <span>☰</span>
            <span>Menu</span>
          </button>

          <!-- Tombol Toggle Sidebar Desktop -->
          <button
            @click="isSidebarOpenDesktop = !isSidebarOpenDesktop"
            type="button"
            :title="isSidebarOpenDesktop ? 'Sembunyikan sidebar' : 'Tampilkan sidebar'"
            class="hidden lg:inline-flex items-center gap-1.5 rounded-md border border-border bg-background px-2.5 py-1.5 text-xs font-medium text-foreground hover:bg-muted cursor-pointer"
          >
            <span>☰</span>
            <span>{{ isSidebarOpenDesktop ? "Tutup Sidebar" : "Sidebar" }}</span>
          </button>

          <span class="text-xs text-muted-foreground hidden sm:inline">/</span>
          <span class="text-xs font-medium text-foreground hidden sm:inline">
            {{ activePage === "tasks" ? "Tugas Aktif" : "Tong Sampah" }}
          </span>
        </div>

        <span class="text-xs font-mono text-muted-foreground"> Selesai: {{ taskCounts.Done }}/{{ taskCounts.All }} </span>
      </div>

      <main class="flex-1 max-w-5xl w-full mx-auto py-7 px-4 sm:px-8">
        <!-- Header Halaman -->
        <header class="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h1 class="text-xl font-bold tracking-tight text-foreground">
              {{ activePage === "tasks" ? "Tugas Aktif" : "Tong Sampah" }}
            </h1>
            <p class="text-xs text-muted-foreground mt-0.5">
              {{ activePage === "tasks" ? "Kelola daftar pekerjaan, pantau progres, dan atur alur kerja." : "Pulihkan tugas yang terhapus atau bersihkan secara permanen." }}
            </p>
          </div>

          <!-- View Switcher (List vs Board) khusus halaman Tugas Aktif -->
          <div v-if="activePage === 'tasks'" class="inline-flex self-start sm:self-center rounded-md border border-border bg-card p-1 shadow-2xs">
            <button
              @click="handleSwitchViewMode('list')"
              type="button"
              class="rounded-sm px-3 py-1 text-xs font-medium transition cursor-pointer"
              :class="viewMode === 'list' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'"
            >
              ☰ List
            </button>
            <button
              @click="handleSwitchViewMode('board')"
              type="button"
              class="rounded-sm px-3 py-1 text-xs font-medium transition cursor-pointer"
              :class="viewMode === 'board' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'"
            >
              ▦ Board
            </button>
          </div>
        </header>

        <!-- Banner Error Koneksi -->
        <div v-if="errorMessage" class="mb-5 rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive flex items-center justify-between">
          <span>{{ errorMessage }}</span>
          <button @click="fetchAllData" class="ml-4 text-xs font-semibold underline cursor-pointer">Coba Lagi</button>
        </div>

        <!-- HALAMAN 1: TUGAS AKTIF -->
        <template v-if="activePage === 'tasks'">
          <TaskForm @add-task="handleAddTask" />

          <!-- Toolbar Filter (Mode List), Search & Sort -->
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-4">
            <div v-if="viewMode === 'list'" class="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
              <button
                v-for="filter in filterOptions"
                :key="filter"
                @click="activeFilter = filter"
                class="px-3 py-1.5 rounded-md text-xs font-medium transition cursor-pointer whitespace-nowrap"
                :class="activeFilter === filter ? 'bg-primary text-primary-foreground shadow-2xs' : 'bg-card text-muted-foreground border border-border hover:text-foreground'"
              >
                {{ filter }} ({{ taskCounts[filter] }})
              </button>
            </div>
            <div v-else class="text-xs text-muted-foreground">Seret kartu antar kolom untuk mengubah status secara langsung.</div>

            <div class="flex items-center gap-2">
              <input
                v-model="searchQuery"
                type="search"
                placeholder="Cari tugas..."
                class="w-full sm:w-48 rounded-md border border-input bg-card px-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none"
              />
              <select v-model="sortBy" aria-label="Urutkan tugas" class="rounded-md border border-input bg-card px-2.5 py-1.5 text-xs text-foreground focus:border-primary focus:outline-none cursor-pointer">
                <option value="newest">Terbaru</option>
                <option value="oldest">Terlama</option>
                <option value="completed">Baru Selesai</option>
              </select>
            </div>
          </div>

          <!-- Loading -->
          <div v-if="isLoading" class="text-center py-12 text-xs text-muted-foreground">Memuat daftar tugas...</div>

          <!-- Mode Tampilan List -->
          <template v-else-if="viewMode === 'list'">
            <div v-if="displayedTasks.length === 0" class="bg-card rounded-lg border border-dashed border-border p-10 text-center">
              <p class="text-sm font-medium text-foreground mb-1">
                {{ searchQuery ? `Tidak ada tugas yang cocok dengan "${searchQuery}"` : `Belum ada tugas pada kategori "${activeFilter}"` }}
              </p>
              <p class="text-xs text-muted-foreground">
                {{ searchQuery ? "Coba kata kunci lain atau bersihkan pencarian." : "Tambahkan tugas baru melalui form di atas untuk memulai." }}
              </p>
            </div>

            <div v-else class="space-y-2.5">
              <TaskItem v-for="task in displayedTasks" :key="task.id" :task="task" @update-task="handleUpdateTask" @request-delete="openSoftDeleteModal" />
            </div>
          </template>

          <!-- Mode Tampilan Kanban Board -->
          <KanbanBoard v-else :tasks="displayedTasks" @update-task="handleUpdateTask" @request-delete="openSoftDeleteModal" />
        </template>

        <!-- HALAMAN 2: TONG SAMPAH (RECYCLE BIN) -->
        <TrashView v-else :trashed-tasks="trashedTasks" :is-loading="isLoadingTrash" @restore-task="handleRestoreTask" @request-permanent-delete="openPermanentDeleteModal" @request-empty-trash="openEmptyTrashModal" />
      </main>
    </div>

    <!-- Modal Konfirmasi -->
    <ConfirmModal :is-open="modalState.isOpen" :title="modalState.title" :message="modalState.message" :confirm-text="modalState.confirmText" :is-processing="isProcessingModal" @confirm="handleConfirmModal" @cancel="closeModal" />

    <!-- Toast Notification -->
    <ToastNotification :toast="toast" @close="toast = null" />
  </div>
</template>
