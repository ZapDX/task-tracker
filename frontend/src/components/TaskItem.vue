<script setup>
import { computed, ref } from "vue";

const props = defineProps({
  task: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["update-task", "delete-task"]);

const isEditing = ref(false);
const editTitle = ref(props.task.title);
const editDescription = ref(props.task.description || "");
const isBusy = ref(false);

const statusBadgeClass = computed(() => {
  switch (props.task.status) {
    case "Done":
      return "bg-emerald-50 text-emerald-700 border-emerald-200";
    case "In Progress":
      return "bg-amber-50 text-amber-700 border-amber-200";
    default:
      return "bg-slate-100 text-slate-700 border-slate-200";
  }
});

const handleStatusChange = async (event) => {
  const newStatus = event.target.value;
  if (newStatus === props.task.status) return;

  isBusy.value = true;
  try {
    await emit("update-task", props.task.id, { status: newStatus });
  } finally {
    isBusy.value = false;
  }
};

const startEdit = () => {
  editTitle.value = props.task.title;
  editDescription.value = props.task.description || "";
  isEditing.value = true;
};

const cancelEdit = () => {
  isEditing.value = false;
};

const saveEdit = async () => {
  if (!editTitle.value.trim()) return;

  isBusy.value = true;
  try {
    await emit("update-task", props.task.id, {
      title: editTitle.value.trim(),
      description: editDescription.value.trim(),
    });
    isEditing.value = false;
  } finally {
    isBusy.value = false;
  }
};

const handleDelete = async () => {
  if (!confirm(`Hapus tugas "${props.task.title}"?`)) return;

  isBusy.value = true;
  try {
    await emit("delete-task", props.task.id);
  } finally {
    isBusy.value = false;
  }
};

const formattedDate = computed(() => {
  if (!props.task.created_at) return "";
  return new Date(props.task.created_at).toLocaleString("id-ID", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
});
</script>

<template>
  <div class="bg-white rounded-xl border border-slate-200 p-4 shadow-sm hover:shadow transition flex flex-col sm:flex-row sm:items-start justify-between gap-4" :class="{ 'opacity-60 pointer-events-none': isBusy }">
    <!-- Mode Tampilan Normal -->
    <div v-if="!isEditing" class="flex-1 min-w-0">
      <div class="flex items-center gap-2.5 flex-wrap mb-1">
        <h3 class="text-base font-semibold text-slate-800 break-words" :class="{ 'line-through text-slate-400': task.status === 'Done' }">
          {{ task.title }}
        </h3>
        <span class="text-xs font-medium px-2.5 py-0.5 rounded-full border" :class="statusBadgeClass">
          {{ task.status }}
        </span>
      </div>

      <p v-if="task.description" class="text-sm text-slate-600 whitespace-pre-line mb-2">
        {{ task.description }}
      </p>
      <p v-else class="text-xs italic text-slate-400 mb-2">Tidak ada deskripsi</p>

      <span class="text-xs text-slate-400">Dibuat: {{ formattedDate }}</span>
    </div>

    <!-- Mode Edit Judul & Deskripsi -->
    <div v-else class="flex-1 space-y-2.5">
      <input v-model="editTitle" type="text" class="w-full rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-800 focus:border-indigo-500 focus:outline-none" />
      <textarea v-model="editDescription" rows="2" placeholder="Deskripsi tugas..." class="w-full rounded-lg border border-slate-300 px-3 py-1.5 text-sm text-slate-700 focus:border-indigo-500 focus:outline-none"></textarea>
      <div class="flex items-center gap-2">
        <button @click="saveEdit" type="button" class="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-700 cursor-pointer">Simpan</button>
        <button @click="cancelEdit" type="button" class="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50 cursor-pointer">Batal</button>
      </div>
    </div>

    <!-- Kontrol Status, Edit & Delete -->
    <div class="flex items-center gap-2 self-end sm:self-center shrink-0">
      <select
        :value="task.status"
        @change="handleStatusChange"
        aria-label="Ubah status tugas"
        class="rounded-lg border border-slate-300 bg-slate-50 px-2.5 py-1.5 text-xs font-medium text-slate-700 focus:border-indigo-500 focus:outline-none cursor-pointer"
      >
        <option value="Todo">Todo</option>
        <option value="In Progress">In Progress</option>
        <option value="Done">Done</option>
      </select>

      <button
        v-if="!isEditing"
        @click="startEdit"
        type="button"
        title="Edit tugas"
        class="rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900 cursor-pointer transition"
      >
        Edit
      </button>

      <button @click="handleDelete" type="button" title="Hapus tugas" class="rounded-lg border border-rose-200 bg-rose-50 px-2.5 py-1.5 text-xs font-medium text-rose-600 hover:bg-rose-100 cursor-pointer transition">Hapus</button>
    </div>
  </div>
</template>
