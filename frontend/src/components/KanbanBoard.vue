<script setup>
import { ref } from "vue";

const props = defineProps({
  tasks: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(["update-task", "request-delete"]);

const columns = [
  { status: "Todo", label: "Todo", dotClass: "bg-slate-400" },
  { status: "In Progress", label: "In Progress", dotClass: "bg-primary" },
  { status: "Done", label: "Done", dotClass: "bg-emerald-500" },
];

const draggedTaskId = ref(null);
const dragOverColumn = ref(null);

// State inline edit di kartu Kanban
const editingTaskId = ref(null);
const editTitle = ref("");
const editDescription = ref("");

const getTasksByStatus = (status) => {
  return props.tasks.filter((t) => t.status === status);
};

const onDragStart = (event, task) => {
  draggedTaskId.value = task.id;
  event.dataTransfer.effectAllowed = "move";
  event.dataTransfer.setData("text/plain", String(task.id));
};

const onDragOver = (status) => {
  dragOverColumn.value = status;
};

const onDragLeave = () => {
  dragOverColumn.value = null;
};

const onDrop = async (targetStatus) => {
  const id = draggedTaskId.value;
  draggedTaskId.value = null;
  dragOverColumn.value = null;

  if (!id) return;
  const task = props.tasks.find((t) => t.id === id);
  if (!task || task.status === targetStatus) return;

  await emit("update-task", id, { status: targetStatus });
};

const startEdit = (task) => {
  editingTaskId.value = task.id;
  editTitle.value = task.title;
  editDescription.value = task.description || "";
};

const cancelEdit = () => {
  editingTaskId.value = null;
};

const saveEdit = async (id) => {
  if (!editTitle.value.trim()) return;
  await emit("update-task", id, {
    title: editTitle.value.trim(),
    description: editDescription.value.trim(),
  });
  editingTaskId.value = null;
};

const formatShortDate = (isoString) => {
  if (!isoString) return "";
  return new Date(isoString).toLocaleString("id-ID", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
};
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-start">
    <div
      v-for="col in columns"
      :key="col.status"
      @dragover.prevent="onDragOver(col.status)"
      @dragleave="onDragLeave"
      @drop.prevent="onDrop(col.status)"
      class="rounded-lg border bg-secondary/50 p-3 min-h-[340px] transition"
      :class="dragOverColumn === col.status ? 'border-primary bg-accent/40 ring-2 ring-ring/20' : 'border-border'"
    >
      <!-- Header Kolom -->
      <div class="flex items-center justify-between mb-3 px-1">
        <div class="flex items-center gap-2">
          <span class="h-2 w-2 rounded-full" :class="col.dotClass"></span>
          <h3 class="text-xs font-semibold text-foreground">{{ col.label }}</h3>
        </div>
        <span class="rounded-md bg-card px-2 py-0.5 text-[11px] font-mono text-muted-foreground border border-border">
          {{ getTasksByStatus(col.status).length }}
        </span>
      </div>

      <!-- Empty Kolom -->
      <div v-if="getTasksByStatus(col.status).length === 0" class="rounded-md border border-dashed border-border/80 py-8 px-3 text-center text-[11px] text-muted-foreground">Seret tugas ke kolom {{ col.label }}</div>

      <!-- Daftar Kartu -->
      <div v-else class="space-y-2.5">
        <div
          v-for="task in getTasksByStatus(col.status)"
          :key="task.id"
          :draggable="editingTaskId !== task.id"
          @dragstart="onDragStart($event, task)"
          class="rounded-lg border border-border bg-card p-3.5 shadow-2xs hover:shadow-sm transition cursor-grab active:cursor-grabbing"
          :class="{ 'opacity-50': draggedTaskId === task.id }"
        >
          <!-- Mode Normal -->
          <template v-if="editingTaskId !== task.id">
            <div class="flex items-start justify-between gap-2 mb-1">
              <span class="text-[11px] font-mono text-muted-foreground">#{{ task.id }}</span>
              <div class="flex items-center gap-1">
                <button @click="startEdit(task)" type="button" class="rounded px-1.5 py-0.5 text-[11px] text-muted-foreground hover:bg-muted hover:text-foreground cursor-pointer">Edit</button>
                <button @click="emit('request-delete', task)" type="button" class="rounded px-1.5 py-0.5 text-[11px] text-destructive hover:bg-destructive/10 cursor-pointer">Hapus</button>
              </div>
            </div>

            <h4 class="text-sm font-semibold text-card-foreground break-words mb-1" :class="{ 'line-through text-muted-foreground': task.status === 'Done' }">
              {{ task.title }}
            </h4>

            <p v-if="task.description" class="text-xs text-muted-foreground line-clamp-3 whitespace-pre-line mb-2.5">
              {{ task.description }}
            </p>

            <div v-if="task.status === 'Done' && task.completed_at" class="mb-2.5 inline-block rounded-sm bg-emerald-50 px-2 py-0.5 text-[11px] font-medium text-emerald-700">✓ Selesai: {{ formatShortDate(task.completed_at) }}</div>

            <div class="flex items-center justify-between pt-2 border-t border-border/60">
              <span class="text-[11px] text-muted-foreground">
                {{ formatShortDate(task.created_at) }}
              </span>
              <select
                :value="task.status"
                @change="emit('update-task', task.id, { status: $event.target.value })"
                aria-label="Pindah status"
                class="rounded border border-input bg-muted px-1.5 py-0.5 text-[11px] text-foreground cursor-pointer"
              >
                <option value="Todo">Todo</option>
                <option value="In Progress">In Progress</option>
                <option value="Done">Done</option>
              </select>
            </div>
          </template>

          <!-- Mode Inline Edit -->
          <template v-else>
            <div class="space-y-2">
              <input v-model="editTitle" type="text" class="w-full rounded border border-input bg-background px-2.5 py-1 text-xs font-medium text-foreground focus:border-primary focus:outline-none" />
              <textarea v-model="editDescription" rows="2" class="w-full rounded border border-input bg-background px-2.5 py-1 text-xs text-foreground focus:border-primary focus:outline-none"></textarea>
              <div class="flex justify-end gap-1.5">
                <button @click="cancelEdit" type="button" class="rounded border border-border bg-secondary px-2.5 py-1 text-[11px] font-medium text-secondary-foreground cursor-pointer">Batal</button>
                <button @click="saveEdit(task.id)" type="button" class="rounded bg-primary px-2.5 py-1 text-[11px] font-medium text-primary-foreground cursor-pointer">Simpan</button>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>
