<script setup>
import { ref } from "vue";

const props = defineProps({
  tasks: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(["update-task", "request-delete", "open-detail"]);

const columns = [
  { status: "Todo", label: "Todo", dotClass: "bg-slate-400" },
  { status: "In Progress", label: "In Progress", dotClass: "bg-primary" },
  { status: "Done", label: "Done", dotClass: "bg-emerald-500" },
];

const draggedTaskId = ref(null);
const dragOverColumn = ref(null);

const getTasksByStatus = (status) => {
  return props.tasks.filter((t) => t.status === status);
};

const getTodayStr = () => {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const d = String(now.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
};

const isOverdue = (task) => {
  if (!task.due_date || task.status === "Done") return false;
  return task.due_date < getTodayStr();
};

const formatShortDueDate = (dateStr) => {
  if (!dateStr) return "";
  const [year, month, day] = dateStr.split("-").map(Number);
  return new Date(year, month - 1, day).toLocaleDateString("id-ID", {
    day: "2-digit",
    month: "short",
  });
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
          draggable="true"
          @dragstart="onDragStart($event, task)"
          @click="emit('open-detail', task)"
          class="group rounded-lg border bg-card p-3.5 shadow-2xs hover:border-primary/40 hover:shadow-sm transition cursor-pointer"
          :class="[isOverdue(task) ? 'border-destructive/40' : 'border-border', { 'opacity-50': draggedTaskId === task.id }]"
        >
          <div class="flex items-start justify-between gap-2 mb-1">
            <div class="flex items-center gap-1.5">
              <span class="text-[11px] font-mono text-muted-foreground">#{{ task.id }}</span>
              <span v-if="isOverdue(task)" class="rounded-sm bg-destructive/10 px-1.5 py-0.5 text-[10px] font-semibold text-destructive"> Overdue </span>
            </div>

            <button @click.stop="emit('request-delete', task)" type="button" class="rounded px-1.5 py-0.5 text-[11px] text-destructive hover:bg-destructive/10 cursor-pointer">Hapus</button>
          </div>

          <h4 class="text-sm font-semibold text-card-foreground group-hover:text-primary transition break-words mb-1" :class="{ 'line-through text-muted-foreground': task.status === 'Done' }">
            {{ task.title }}
          </h4>

          <p v-if="task.description" class="text-xs text-muted-foreground line-clamp-2 whitespace-pre-line mb-2.5">
            {{ task.description }}
          </p>

          <div class="flex flex-wrap gap-1.5 mb-2.5">
            <span v-if="task.due_date" class="inline-block rounded-sm px-2 py-0.5 text-[11px] font-medium" :class="isOverdue(task) ? 'bg-destructive/10 text-destructive' : 'bg-secondary text-secondary-foreground'">
              Due: {{ formatShortDueDate(task.due_date) }}
            </span>

            <span v-if="task.status === 'Done' && task.completed_at" class="inline-block rounded-sm bg-emerald-50 px-2 py-0.5 text-[11px] font-medium text-emerald-700"> Selesai: {{ formatShortDate(task.completed_at) }} </span>
          </div>

          <div @click.stop class="flex items-center justify-between pt-2 border-t border-border/60">
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
        </div>
      </div>
    </div>
  </div>
</template>
