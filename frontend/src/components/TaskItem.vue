<script setup>
import { computed, ref } from "vue";

const props = defineProps({
  task: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["update-task", "request-delete"]);

const isEditing = ref(false);
const editTitle = ref(props.task.title);
const editDescription = ref(props.task.description || "");
const isBusy = ref(false);

const statusBadgeClass = computed(() => {
  switch (props.task.status) {
    case "Done":
      return "bg-emerald-50 text-emerald-700 border-emerald-200";
    case "In Progress":
      return "bg-accent text-accent-foreground border-primary/20";
    default:
      return "bg-secondary text-secondary-foreground border-border";
  }
});

const formatDateTime = (isoString) => {
  if (!isoString) return "";
  return new Date(isoString).toLocaleString("id-ID", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const formattedCreatedAt = computed(() => formatDateTime(props.task.created_at));
const formattedCompletedAt = computed(() => formatDateTime(props.task.completed_at));

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
</script>

<template>
  <div class="bg-card rounded-lg border border-border p-4 shadow-2xs hover:shadow-sm transition flex flex-col sm:flex-row sm:items-start justify-between gap-4" :class="{ 'opacity-60 pointer-events-none': isBusy }">
    <!-- Mode Tampilan Normal -->
    <div v-if="!isEditing" class="flex-1 min-w-0">
      <div class="flex items-center gap-2 flex-wrap mb-1.5">
        <span class="text-xs font-mono text-muted-foreground">#{{ task.id }}</span>
        <h3 class="text-sm font-semibold text-card-foreground break-words" :class="{ 'line-through text-muted-foreground': task.status === 'Done' }">
          {{ task.title }}
        </h3>
        <span class="text-[11px] font-medium px-2 py-0.5 rounded-md border" :class="statusBadgeClass">
          {{ task.status }}
        </span>
      </div>

      <p v-if="task.description" class="text-sm text-muted-foreground whitespace-pre-line mb-2.5 leading-relaxed">
        {{ task.description }}
      </p>
      <p v-else class="text-xs italic text-muted-foreground/70 mb-2.5">Tidak ada deskripsi</p>

      <div class="flex items-center gap-3 flex-wrap text-[11px] text-muted-foreground">
        <span>Dibuat: {{ formattedCreatedAt }}</span>
        <span v-if="task.status === 'Done' && formattedCompletedAt" class="inline-flex items-center gap-1 font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-sm"> ✓ Selesai: {{ formattedCompletedAt }} </span>
      </div>
    </div>

    <!-- Mode Edit -->
    <div v-else class="flex-1 space-y-2.5">
      <input v-model="editTitle" type="text" class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-sm font-medium text-foreground focus:border-primary focus:outline-none" />
      <textarea v-model="editDescription" rows="2" placeholder="Deskripsi tugas..." class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-sm text-foreground focus:border-primary focus:outline-none"></textarea>
      <div class="flex items-center gap-2">
        <button @click="saveEdit" type="button" class="rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:opacity-90 cursor-pointer">Simpan</button>
        <button @click="cancelEdit" type="button" class="rounded-md border border-border bg-secondary px-3 py-1.5 text-xs font-medium text-secondary-foreground hover:bg-muted cursor-pointer">Batal</button>
      </div>
    </div>

    <!-- Kontrol Aksi -->
    <div class="flex items-center gap-2 self-end sm:self-center shrink-0">
      <select
        :value="task.status"
        @change="handleStatusChange"
        aria-label="Ubah status tugas"
        class="rounded-md border border-input bg-muted px-2.5 py-1.5 text-xs font-medium text-foreground focus:border-primary focus:outline-none cursor-pointer"
      >
        <option value="Todo">Todo</option>
        <option value="In Progress">In Progress</option>
        <option value="Done">Done</option>
      </select>

      <button v-if="!isEditing" @click="startEdit" type="button" class="rounded-md border border-border bg-background px-2.5 py-1.5 text-xs font-medium text-foreground hover:bg-muted cursor-pointer transition">Edit</button>

      <button @click="emit('request-delete', task)" type="button" class="rounded-md border border-destructive/25 bg-destructive/5 px-2.5 py-1.5 text-xs font-medium text-destructive hover:bg-destructive/10 cursor-pointer transition">
        Hapus
      </button>
    </div>
  </div>
</template>
