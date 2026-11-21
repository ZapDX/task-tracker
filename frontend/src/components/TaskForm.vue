<script setup>
import { ref } from "vue";

const emit = defineEmits(["add-task"]);

const title = ref("");
const description = ref("");
const status = ref("Todo");
const dueDate = ref("");
const isSubmitting = ref(false);
const validationError = ref("");

const handleSubmit = async () => {
  validationError.value = "";

  if (!title.value.trim()) {
    validationError.value = "Judul tugas wajib diisi.";
    return;
  }

  isSubmitting.value = true;
  try {
    await emit("add-task", {
      title: title.value.trim(),
      description: description.value.trim(),
      status: status.value,
      due_date: dueDate.value || null,
    });
    title.value = "";
    description.value = "";
    status.value = "Todo";
    dueDate.value = "";
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <form @submit.prevent="handleSubmit" @keydown.ctrl.enter.prevent="handleSubmit" @keydown.meta.enter.prevent="handleSubmit" class="bg-card rounded-lg shadow-2xs border border-border p-5 mb-6">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-sm font-semibold text-card-foreground">Tugas Baru</h2>
      <span class="text-xs font-mono text-muted-foreground">POST /tasks</span>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
      <div class="md:col-span-2">
        <label class="block text-xs font-medium text-muted-foreground mb-1.5"> Judul Tugas <span class="text-destructive">*</span> </label>
        <input
          v-model="title"
          type="text"
          placeholder="Tulis judul tugas..."
          class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-ring/20 transition"
        />
        <p v-if="validationError" class="text-xs text-destructive mt-1">
          {{ validationError }}
        </p>
      </div>

      <div>
        <label class="block text-xs font-medium text-muted-foreground mb-1.5"> Status Awal </label>
        <select v-model="status" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-ring/20 transition cursor-pointer">
          <option value="Todo">Todo</option>
          <option value="In Progress">In Progress</option>
          <option value="Done">Done</option>
        </select>
      </div>

      <div>
        <label class="block text-xs font-medium text-muted-foreground mb-1.5"> Deadline <span class="opacity-70">(opsional)</span> </label>
        <input v-model="dueDate" type="date" class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-ring/20 transition cursor-pointer" />
      </div>
    </div>

    <div class="mb-4">
      <label class="block text-xs font-medium text-muted-foreground mb-1.5"> Deskripsi <span class="opacity-70">(opsional)</span> </label>
      <textarea
        v-model="description"
        rows="2"
        placeholder="Tambahkan catatan atau detail pekerjaan..."
        class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-ring/20 transition"
      ></textarea>
    </div>

    <div class="flex items-center justify-between gap-2">
      <button
        type="submit"
        :disabled="isSubmitting"
        title="Simpan tugas (Ctrl + Enter)"
        class="ml-auto inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-xs font-medium text-primary-foreground shadow-2xs hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-ring/30 disabled:opacity-50 cursor-pointer transition"
      >
        {{ isSubmitting ? "Menyimpan..." : "+ Tambah Tugas" }}
      </button>
    </div>
  </form>
</template>
