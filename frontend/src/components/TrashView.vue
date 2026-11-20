<script setup>
defineProps({
  trashedTasks: {
    type: Array,
    required: true,
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["restore-task", "request-permanent-delete", "request-empty-trash"]);

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
</script>

<template>
  <div>
    <!-- Banner Info Retensi & Tombol Kosongkan -->
    <div class="mb-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-lg border border-border bg-card p-4 shadow-2xs">
      <div>
        <h2 class="text-sm font-semibold text-card-foreground">Tong Sampah (Recycle Bin)</h2>
        <p class="text-xs text-muted-foreground mt-0.5">Item di tong sampah akan dihapus secara permanen secara otomatis setelah 30 hari.</p>
      </div>

      <button
        v-if="trashedTasks.length > 0"
        @click="emit('request-empty-trash')"
        type="button"
        class="self-start sm:self-center rounded-md border border-destructive/30 bg-destructive/10 px-3.5 py-2 text-xs font-medium text-destructive hover:bg-destructive/15 cursor-pointer transition shrink-0"
      >
        Kosongkan Tong Sampah
      </button>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="text-center py-12 text-xs text-muted-foreground">Memuat isi tong sampah...</div>

    <!-- Empty Trash -->
    <div v-else-if="trashedTasks.length === 0" class="rounded-lg border border-dashed border-border bg-card p-12 text-center">
      <p class="text-sm font-medium text-foreground mb-1">Tong sampah kosong</p>
      <p class="text-xs text-muted-foreground">Tugas yang kamu hapus akan muncul di sini dan dapat dipulihkan kapan saja dalam 30 hari.</p>
    </div>

    <!-- Daftar Item Terhapus -->
    <div v-else class="space-y-2.5">
      <div v-for="task in trashedTasks" :key="task.id" class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-lg border border-border bg-card p-4 shadow-2xs">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 flex-wrap mb-1">
            <span class="text-xs font-mono text-muted-foreground">#{{ task.id }}</span>
            <h3 class="text-sm font-semibold text-card-foreground break-words">
              {{ task.title }}
            </h3>
            <span class="rounded-md border px-2 py-0.5 text-[11px] font-medium" :class="task.days_remaining <= 3 ? 'border-destructive/30 bg-destructive/10 text-destructive' : 'border-amber-200 bg-amber-50 text-amber-800'">
              Sisa {{ task.days_remaining }} hari
            </span>
          </div>

          <p v-if="task.description" class="text-xs text-muted-foreground line-clamp-2 mb-1.5">
            {{ task.description }}
          </p>

          <div class="flex items-center gap-3 text-[11px] text-muted-foreground">
            <span>Status terakhir: {{ task.status }}</span>
            <span>•</span>
            <span>Dihapus pada: {{ formatDateTime(task.deleted_at) }}</span>
          </div>
        </div>

        <div class="flex items-center gap-2 self-end sm:self-center shrink-0">
          <button @click="emit('restore-task', task.id)" type="button" class="rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:opacity-90 cursor-pointer transition">Pulihkan</button>
          <button
            @click="emit('request-permanent-delete', task)"
            type="button"
            class="rounded-md border border-destructive/25 bg-destructive/5 px-3 py-1.5 text-xs font-medium text-destructive hover:bg-destructive/10 cursor-pointer transition"
          >
            Hapus Permanen
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
