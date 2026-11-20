<script setup>
defineProps({
  toast: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(["close"]);
</script>

<template>
  <Transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="translate-y-2 opacity-0"
    enter-to-class="translate-y-0 opacity-100"
    leave-active-class="transition duration-150 ease-in"
    leave-from-class="translate-y-0 opacity-100"
    leave-to-class="translate-y-2 opacity-0"
  >
    <div
      v-if="toast"
      class="fixed bottom-5 right-5 z-50 flex items-center gap-3 rounded-lg border px-4 py-3 shadow-md text-sm"
      :class="toast.type === 'error' ? 'bg-card border-destructive/30 text-destructive' : 'bg-card border-border text-foreground'"
    >
      <span class="h-2 w-2 rounded-full shrink-0" :class="toast.type === 'error' ? 'bg-destructive' : 'bg-emerald-500'"></span>
      <span class="font-medium">{{ toast.message }}</span>
      <button @click="emit('close')" class="ml-2 text-xs text-muted-foreground hover:text-foreground cursor-pointer" aria-label="Tutup notifikasi">✕</button>
    </div>
  </Transition>
</template>
