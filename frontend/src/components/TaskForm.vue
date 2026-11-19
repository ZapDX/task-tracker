<script setup>
import { ref } from "vue";

const emit = defineEmits(["add-task"]);

const title = ref("");
const description = ref("");
const status = ref("Todo");
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
    });
    // Reset form setelah berhasil ditambahkan
    title.value = "";
    description.value = "";
    status.value = "Todo";
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <form @submit.prevent="handleSubmit" class="bg-white rounded-xl shadow-sm border border-slate-200 p-5 mb-6">
    <h2 class="text-base font-semibold text-slate-800 mb-4">Tambah Tugas Baru</h2>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
      <div class="md:col-span-2">
        <label class="block text-xs font-medium text-slate-600 mb-1"> Judul Tugas <span class="text-rose-500">*</span> </label>
        <input
          v-model="title"
          type="text"
          placeholder="Contoh: Integrasi endpoint REST API..."
          class="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-800 placeholder-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
        />
        <p v-if="validationError" class="text-xs text-rose-600 mt-1">
          {{ validationError }}
        </p>
      </div>

      <div>
        <label class="block text-xs font-medium text-slate-600 mb-1">Status Awal</label>
        <select v-model="status" class="w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-sm text-slate-800 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20">
          <option value="Todo">Todo</option>
          <option value="In Progress">In Progress</option>
          <option value="Done">Done</option>
        </select>
      </div>
    </div>

    <div class="mb-4">
      <label class="block text-xs font-medium text-slate-600 mb-1"> Deskripsi <span class="text-slate-400">(opsional)</span> </label>
      <textarea
        v-model="description"
        rows="2"
        placeholder="Tambahkan detail atau catatan tugas..."
        class="w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-800 placeholder-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
      ></textarea>
    </div>

    <div class="flex justify-end">
      <button
        type="submit"
        :disabled="isSubmitting"
        class="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-5 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 cursor-pointer transition"
      >
        {{ isSubmitting ? "Menyimpan..." : "+ Tambah Tugas" }}
      </button>
    </div>
  </form>
</template>
