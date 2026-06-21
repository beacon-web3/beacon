<script setup lang="ts">
defineProps<{
  icon: string
  title: string
  description: string
}>()
</script>

<template>
  <article class="beacon-panel p-6 sm:p-7">
    <div class="grid size-11 place-items-center rounded-md border border-rule bg-vellum text-beacon-700 dark:text-beacon-200">
      <UIcon
        :name="icon"
        class="size-5"
      />
    </div>

    <h3 class="mt-5 text-xl font-semibold tracking-[-0.03em] text-ink">
      {{ title }}
    </h3>
    <p class="mt-3 text-sm leading-7 text-ink-muted">
      {{ description }}
    </p>
  </article>
</template>
