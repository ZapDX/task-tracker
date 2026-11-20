<script setup>
import { computed, ref } from "vue";

const props = defineProps({
  task: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["update-task", "request-delete", "open-detail"]);

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

const getTodayStr = () => {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const d = String(now.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
};

const isOverdue = computed(() => {
  if (!props.task.due_date || props.task.status === "Done") return false;
  return props.task.due_date < getTodayStr();
});

const isDueToday = computed(() => {
  if (!props.task.due_date || props.task.status === "Done") return false;
  return props.task.due_date === getTodayStr();
});

const formattedDueDate = computed(() => {
  if (!props.task.due_date) return "";
  const [year, month, day] = props.task.due_date.split("-").map(Number);
  return new Date(year, month - 1, day).toLocaleDateString("id-ID", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
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
</script>

<template>
  <div
    @click="emit('open-detail', task)"
    class="group bg-card rounded-lg border p-4 shadow-2xs hover:border-primary/40 hover:shadow-sm transition cursor-pointer flex flex-col sm:flex-row sm:items-start justify-between gap-4"
    :class="[isOverdue ? 'border-destructive/40' : 'border-border', { 'opacity-60 pointer-events-none': isBusy }]"
  >
    <!-- Konten Tugas -->
    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-2 flex-wrap mb-1.5">
        <span class="text-xs font-mono text-muted-foreground">#{{ task.id }}</span>
        <h3 class="text-sm font-semibold text-card-foreground group-hover:text-primary transition break-words" :class="{ 'line-through text-muted-foreground': task.status === 'Done' }">
          {{ task.title }}
        </h3>
        <span class="text-[11px] font-medium px-2 py-0.5 rounded-md border" :class="statusBadgeClass">
          {{ task.status }}
        </span>
        <span v-if="isOverdue" class="text-[11px] font-semibold px-2 py-0.5 rounded-md border border-destructive/25 bg-destructive/10 text-destructive"> Overdue </span>
      </div>

      <p v-if="task.description" class="text-sm text-muted-foreground line-clamp-2 whitespace-pre-line mb-2.5 leading-relaxed">
        {{ task.description }}
      </p>
      <p v-else class="text-xs italic text-muted-foreground/70 mb-2.5">Tidak ada deskripsi</p>

      <div class="flex items-center gap-3 flex-wrap text-[11px] text-muted-foreground">
        <span>Dibuat: {{ formattedCreatedAt }}</span>

        <span
          v-if="task.due_date"
          class="inline-flex items-center gap-1 rounded-sm px-2 py-0.5 font-medium"
          :class="isOverdue ? 'bg-destructive/10 text-destructive' : isDueToday ? 'bg-amber-50 text-amber-800' : 'bg-secondary text-secondary-foreground'"
        >
          Deadline: {{ formattedDueDate }}
        </span>

        <span v-if="task.status === 'Done' && formattedCompletedAt" class="inline-flex items-center gap-1 font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-sm"> Selesai: {{ formattedCompletedAt }} </span>
      </div>
    </div>

    <!-- Kontrol Cepat -->
    <div @click.stop class="flex items-center gap-2 self-end sm:self-center shrink-0">
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

      <button @click="emit('open-detail', task)" type="button" class="rounded-md border border-border bg-background px-2.5 py-1.5 text-xs font-medium text-foreground hover:bg-muted cursor-pointer transition">Detail</button>

      <button @click="emit('request-delete', task)" type="button" class="rounded-md border border-destructive/25 bg-destructive/5 px-2.5 py-1.5 text-xs font-medium text-destructive hover:bg-destructive/10 cursor-pointer transition">
        Hapus
      </button>
    </div>
  </div>
</template>
