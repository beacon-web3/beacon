<script setup lang="ts">
defineProps<{
  icon: string
  title: string
  description: string
}>()
</script>

<template>
  <article class="rounded-xl border border-rule bg-paper p-6">
    <div class="mb-6 grid size-10 place-items-center rounded-md bg-vellum text-beacon-700 dark:text-beacon-200">
      <UIcon
        :name="icon"
        class="size-5"
      />
    </div>
    <h3 class="text-lg font-semibold tracking-[-0.02em] text-ink">
      {{ title }}
    </h3>
    <p class="mt-3 text-sm leading-7 text-ink-muted">
      {{ description }}
    </p>
  </article>
</template>
