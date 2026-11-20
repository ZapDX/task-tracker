<script setup>
import { computed } from "vue";

const props = defineProps({
  activePage: {
    type: String,
    required: true,
  },
  activeFilter: {
    type: String,
    required: true,
  },
  taskCounts: {
    type: Object,
    required: true,
  },
  trashCount: {
    type: Number,
    default: 0,
  },
  isOpenMobile: {
    type: Boolean,
    default: false,
  },
  isOpenDesktop: {
    type: Boolean,
    default: true,
  },
});

const emit = defineEmits(["navigate", "select-filter", "close-mobile", "toggle-desktop"]);

const statusFilters = [
  { key: "All", label: "Semua Tugas", dotClass: "bg-foreground/50" },
  { key: "Todo", label: "Todo", dotClass: "bg-slate-400" },
  { key: "In Progress", label: "In Progress", dotClass: "bg-primary" },
  { key: "Done", label: "Done", dotClass: "bg-emerald-500" },
];

const completionRate = computed(() => {
  if (!props.taskCounts.All) return 0;
  return Math.round((props.taskCounts.Done / props.taskCounts.All) * 100);
});

const handleSelectPage = (page) => {
  emit("navigate", page);
  emit("close-mobile");
};

const handleSelectFilter = (filterKey) => {
  emit("navigate", "tasks");
  emit("select-filter", filterKey);
  emit("close-mobile");
};
</script>

<template>
  <!-- Backdrop Mobile -->
  <div v-if="isOpenMobile" class="fixed inset-0 z-40 bg-black/50 backdrop-blur-[1px] lg:hidden" @click="emit('close-mobile')"></div>

  <!-- Sidebar Container -->
  <aside
    class="fixed inset-y-0 left-0 z-50 flex w-64 flex-col bg-sidebar text-sidebar-foreground border-r border-sidebar-border shadow-xl lg:shadow-none lg:sticky lg:top-0 lg:h-screen lg:z-20 transition-all duration-200 shrink-0"
    :class="[isOpenMobile ? 'translate-x-0' : '-translate-x-full', isOpenDesktop ? 'lg:translate-x-0 lg:w-64' : 'lg:translate-x-0 lg:w-0 lg:overflow-hidden lg:border-r-0']"
  >
    <div class="flex h-full w-64 flex-col">
      <!-- Brand Header -->
      <div class="flex items-center justify-between border-b border-sidebar-border px-4 py-3.5 shrink-0">
        <div class="flex items-center gap-2.5">
          <div class="flex h-7 w-7 items-center justify-center rounded-md bg-sidebar-primary text-xs font-bold text-sidebar-primary-foreground">TT</div>
          <div>
            <p class="text-sm font-semibold leading-none tracking-tight">Task Tracker</p>
            <p class="text-[11px] text-muted-foreground mt-1">Workspace</p>
          </div>
        </div>

        <!-- Tombol Tutup Mobile -->
        <button @click="emit('close-mobile')" class="rounded-md p-1.5 text-xs text-muted-foreground hover:bg-sidebar-accent hover:text-foreground lg:hidden cursor-pointer" aria-label="Tutup sidebar">✕</button>

        <!-- Tombol Sembunyikan Sidebar Desktop -->
        <button
          @click="emit('toggle-desktop')"
          title="Sembunyikan sidebar"
          class="hidden lg:inline-flex rounded-md p-1.5 text-xs text-muted-foreground hover:bg-sidebar-accent hover:text-foreground cursor-pointer"
          aria-label="Sembunyikan sidebar"
        >
          «
        </button>
      </div>

      <!-- Ringkasan Progres di Bagian Atas (Langsung Terlihat Tanpa Scroll) -->
      <div class="border-b border-sidebar-border px-3.5 py-3 shrink-0">
        <div class="rounded-md border border-sidebar-border bg-card p-3 shadow-2xs">
          <div class="flex items-center justify-between text-xs mb-1.5">
            <span class="font-medium text-card-foreground">Progres Selesai</span>
            <span class="font-mono font-semibold text-primary">{{ completionRate }}%</span>
          </div>
          <div class="h-1.5 w-full overflow-hidden rounded-full bg-secondary">
            <div class="h-full rounded-full bg-sidebar-primary transition-all duration-300" :style="{ width: `${completionRate}%` }"></div>
          </div>
          <p class="mt-1.5 text-[11px] text-muted-foreground">{{ taskCounts.Done }} dari {{ taskCounts.All }} tugas selesai</p>
        </div>
      </div>

      <!-- Menu & Filter -->
      <div class="flex-1 overflow-y-auto px-3 py-3.5 space-y-5">
        <div>
          <p class="px-2.5 mb-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Menu</p>
          <nav class="space-y-1">
            <button
              @click="handleSelectPage('tasks')"
              class="flex w-full items-center justify-between rounded-md px-2.5 py-2 text-xs font-medium transition cursor-pointer"
              :class="activePage === 'tasks' ? 'bg-sidebar-accent text-sidebar-accent-foreground font-semibold' : 'text-sidebar-foreground hover:bg-sidebar-accent/60'"
            >
              <span class="flex items-center gap-2">
                <span>📋</span>
                <span>Tugas Aktif</span>
              </span>
              <span class="rounded-md bg-background px-1.5 py-0.5 text-[11px] font-mono border border-sidebar-border">
                {{ taskCounts.All }}
              </span>
            </button>

            <button
              @click="handleSelectPage('trash')"
              class="flex w-full items-center justify-between rounded-md px-2.5 py-2 text-xs font-medium transition cursor-pointer"
              :class="activePage === 'trash' ? 'bg-sidebar-accent text-sidebar-accent-foreground font-semibold' : 'text-sidebar-foreground hover:bg-sidebar-accent/60'"
            >
              <span class="flex items-center gap-2">
                <span>🗑️</span>
                <span>Tong Sampah</span>
              </span>
              <span class="rounded-md px-1.5 py-0.5 text-[11px] font-mono border" :class="trashCount > 0 ? 'bg-destructive/10 text-destructive border-destructive/20' : 'bg-background text-muted-foreground border-sidebar-border'">
                {{ trashCount }}
              </span>
            </button>
          </nav>
        </div>

        <!-- Pintasan Filter Status -->
        <div>
          <p class="px-2.5 mb-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Status Tugas</p>
          <div class="space-y-1">
            <button
              v-for="item in statusFilters"
              :key="item.key"
              @click="handleSelectFilter(item.key)"
              class="flex w-full items-center justify-between rounded-md px-2.5 py-1.5 text-xs transition cursor-pointer"
              :class="activePage === 'tasks' && activeFilter === item.key ? 'bg-sidebar-accent/80 text-sidebar-accent-foreground font-medium' : 'text-muted-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-foreground'"
            >
              <span class="flex items-center gap-2">
                <span class="h-2 w-2 rounded-full" :class="item.dotClass"></span>
                <span>{{ item.label }}</span>
              </span>
              <span class="text-[11px] font-mono">{{ taskCounts[item.key] }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>
