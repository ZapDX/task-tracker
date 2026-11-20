<script setup>
defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: "Konfirmasi Hapus",
  },
  message: {
    type: String,
    default: "",
  },
  confirmText: {
    type: String,
    default: "Pindahkan ke Tong Sampah",
  },
  isProcessing: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["confirm", "cancel"]);
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4" @click.self="emit('cancel')">
    <div class="w-full max-w-md rounded-lg border border-border bg-card p-5 shadow-lg">
      <h3 class="text-base font-semibold text-card-foreground mb-1.5">
        {{ title }}
      </h3>
      <p class="text-sm text-muted-foreground leading-relaxed mb-5">
        {{ message }}
      </p>

      <div class="flex items-center justify-end gap-2">
        <button
          type="button"
          :disabled="isProcessing"
          @click="emit('cancel')"
          class="rounded-md border border-border bg-secondary px-3.5 py-2 text-xs font-medium text-secondary-foreground hover:bg-muted cursor-pointer transition disabled:opacity-50"
        >
          Batal
        </button>
        <button type="button" :disabled="isProcessing" @click="emit('confirm')" class="rounded-md bg-destructive px-3.5 py-2 text-xs font-medium text-destructive-foreground hover:opacity-90 cursor-pointer transition disabled:opacity-50">
          {{ isProcessing ? "Memproses..." : confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>
