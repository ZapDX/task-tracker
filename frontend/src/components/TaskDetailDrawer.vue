<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  task: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['close', 'update-task', 'request-delete'])

const editTitle = ref('')
const editDescription = ref('')
const editStatus = ref('Todo')
const editDueDate = ref('')
const isSaving = ref(false)
const validationError = ref('')

const syncFormWithTask = (task) => {
  if (!task) return
  editTitle.value = task.title
  editDescription.value = task.description || ''
  editStatus.value = task.status
  editDueDate.value = task.due_date || ''
  validationError.value = ''
}

watch(
  () => props.task,
  (newTask) => {
    syncFormWithTask(newTask)
  },
  { immediate: true, deep: true }
)

const hasChanges = computed(() => {
  if (!props.task) return false
  return (
    editTitle.value.trim() !== props.task.title ||
    editDescription.value.trim() !== (props.task.description || '') ||
    editStatus.value !== props.task.status ||
    (editDueDate.value || null) !== (props.task.due_date || null)
  )
})

const getTodayStr = () => {
  const now = new Date()
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const deadlineState = computed(() => {
  if (!editDueDate.value || editStatus.value === 'Done') return null
  const today = getTodayStr()
  if (editDueDate.value < today) return 'overdue'
  if (editDueDate.value === today) return 'today'
  return 'upcoming'
})

const formatDateTime = (isoString) => {
  if (!isoString) return '-'
  return new Date(isoString).toLocaleString('id-ID', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const handleSave = async () => {
  if (!hasChanges.value || isSaving.value) return
  validationError.value = ''
  if (!editTitle.value.trim()) {
    validationError.value = 'Judul tugas tidak boleh kosong.'
    return
  }

  isSaving.value = true
  try {
    await emit('update-task', props.task.id, {
      title: editTitle.value.trim(),
      description: editDescription.value.trim(),
      status: editStatus.value,
      due_date: editDueDate.value || null,
    })
  } finally {
    isSaving.value = false
  }
}

const handleDeleteClick = () => {
  const target = props.task
  emit('close')
  emit('request-delete', target)
}
</script>

<template>
  <Transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition duration-150 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="task"
      class="fixed inset-0 z-50 flex justify-end bg-black/35 backdrop-blur-[1px]"
      @click.self="emit('close')"
    >
      <aside
        @keydown.ctrl.enter.prevent="handleSave"
        @keydown.meta.enter.prevent="handleSave"
        class="flex h-full w-full max-w-xl flex-col border-l border-border bg-card text-card-foreground shadow-2xl"
      >
        <!-- Header Drawer -->
        <div class="flex items-center justify-between border-b border-border px-6 py-3.5 shrink-0">
          <div class="flex items-center gap-2 text-xs text-muted-foreground">
            <span class="rounded bg-muted px-2 py-0.5 font-mono font-medium text-foreground">
              #{{ task.id }}
            </span>
            <span>Detail Tugas</span>
          </div>

          <div class="flex items-center gap-1.5">
            <button
              @click="handleDeleteClick"
              type="button"
              title="Pindahkan ke tong sampah"
              class="inline-flex items-center gap-1.5 rounded-md border border-destructive/25 bg-destructive/5 px-2.5 py-1.5 text-xs font-medium text-destructive hover:bg-destructive/10 cursor-pointer transition"
            >
              <svg
                class="h-3.5 w-3.5"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.75"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M3 6h18" />
                <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
                <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
              </svg>
              <span>Hapus</span>
            </button>

            <button
              @click="emit('close')"
              type="button"
              aria-label="Tutup panel detail"
              class="rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground cursor-pointer transition"
            >
              <svg
                class="h-4 w-4"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.75"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M18 6 6 18" />
                <path d="m6 6 12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Konten Utama Drawer -->
        <div class="flex-1 overflow-y-auto px-6 py-5 space-y-6">
          <div>
            <label class="sr-only">Judul Tugas</label>
            <input
              v-model="editTitle"
              type="text"
              placeholder="Judul tugas..."
              class="w-full border-0 border-b border-transparent bg-transparent pb-1 text-lg font-bold tracking-tight text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none transition"
            />
            <p v-if="validationError" class="mt-1 text-xs text-destructive">
              {{ validationError }}
            </p>
          </div>

          <!-- Tabel Properti Terstruktur -->
          <div class="rounded-lg border border-border bg-muted/40 divide-y divide-border text-xs">
            <div class="flex items-center justify-between px-4 py-2.5">
              <span class="text-muted-foreground font-medium">Status</span>
              <select
                v-model="editStatus"
                class="rounded-md border border-input bg-card px-2.5 py-1 text-xs font-medium text-foreground focus:border-primary focus:outline-none cursor-pointer"
              >
                <option value="Todo">Todo</option>
                <option value="In Progress">In Progress</option>
                <option value="Done">Done</option>
              </select>
            </div>

            <div class="flex items-center justify-between gap-2 px-4 py-2.5">
              <span class="text-muted-foreground font-medium">Deadline</span>
              <div class="flex items-center gap-2">
                <span
                  v-if="deadlineState === 'overdue'"
                  class="rounded-sm bg-destructive/10 px-2 py-0.5 text-[11px] font-semibold text-destructive border border-destructive/20"
                >
                  Overdue
                </span>
                <span
                  v-else-if="deadlineState === 'today'"
                  class="rounded-sm bg-amber-50 px-2 py-0.5 text-[11px] font-medium text-amber-800 border border-amber-200"
                >
                  Hari ini
                </span>

                <input
                  v-model="editDueDate"
                  type="date"
                  class="rounded-md border border-input bg-card px-2.5 py-1 text-xs text-foreground focus:border-primary focus:outline-none cursor-pointer"
                />

                <button
                  v-if="editDueDate"
                  @click="editDueDate = ''"
                  type="button"
                  title="Hapus deadline"
                  class="text-[11px] text-muted-foreground hover:text-destructive cursor-pointer"
                >
                  Reset
                </button>
              </div>
            </div>

            <div class="flex items-center justify-between px-4 py-2.5">
              <span class="text-muted-foreground font-medium">Dibuat pada</span>
              <span class="text-foreground">{{ formatDateTime(task.created_at) }}</span>
            </div>

            <div class="flex items-center justify-between px-4 py-2.5">
              <span class="text-muted-foreground font-medium">Selesai pada</span>
              <span
                :class="
                  task.status === 'Done' && task.completed_at
                    ? 'font-medium text-emerald-700'
                    : 'text-muted-foreground'
                "
              >
                {{ task.status === 'Done' ? formatDateTime(task.completed_at) : '-' }}
              </span>
            </div>
          </div>

          <!-- Area Deskripsi Luas -->
          <div class="flex-1 flex flex-col">
            <div class="flex items-center justify-between mb-2">
              <label class="text-xs font-semibold text-foreground">
                Deskripsi & Catatan Detail
              </label>
              <span class="text-[11px] text-muted-foreground">
                {{ editDescription.length }} karakter
              </span>
            </div>
            <textarea
              v-model="editDescription"
              rows="11"
              placeholder="Tulis rincian pekerjaan, catatan rapat, atau daftar poin di sini..."
              class="w-full rounded-lg border border-input bg-background p-3.5 text-sm text-foreground leading-relaxed placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-ring/20 transition"
            ></textarea>
          </div>
        </div>

        <!-- Footer Aksi Simpan -->
        <div
          class="flex items-center justify-between border-t border-border bg-muted/30 px-6 py-3.5 shrink-0"
        >
          <span class="text-xs text-muted-foreground">
            {{ hasChanges ? 'Ada perubahan belum disimpan (Ctrl + Enter)' : 'Semua perubahan tersimpan' }}
          </span>

          <div class="flex items-center gap-2">
            <button
              v-if="hasChanges"
              @click="syncFormWithTask(task)"
              type="button"
              :disabled="isSaving"
              class="rounded-md border border-border bg-secondary px-3 py-1.5 text-xs font-medium text-secondary-foreground hover:bg-muted cursor-pointer transition"
            >
              Batal
            </button>
            <button
              @click="handleSave"
              type="button"
              :disabled="isSaving || !hasChanges"
              title="Simpan perubahan (Ctrl + Enter)"
              class="rounded-md bg-primary px-4 py-1.5 text-xs font-medium text-primary-foreground shadow-2xs hover:opacity-90 disabled:opacity-40 cursor-pointer transition"
            >
              {{ isSaving ? 'Menyimpan...' : 'Simpan Perubahan' }}
            </button>
          </div>
        </div>
      </aside>
    </div>
  </Transition>
</template>