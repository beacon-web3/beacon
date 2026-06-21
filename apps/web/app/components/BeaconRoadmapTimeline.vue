<script setup lang="ts">
defineProps<{
  phases: Array<{
    phase: string
    title: string
    description: string
  }>
}>()
</script>

<template>
  <ol class="space-y-4">
    <li
      v-for="phase in phases"
      :key="phase.phase"
      class="beacon-panel p-5"
    >
      <div class="flex flex-col gap-3 sm:flex-row sm:items-start">
        <p class="beacon-kicker min-w-28">
          {{ phase.phase }}
        </p>
        <div>
          <h3 class="text-lg font-semibold tracking-[-0.02em] text-ink">
            {{ phase.title }}
          </h3>
          <p class="mt-2 text-sm leading-7 text-ink-muted">
            {{ phase.description }}
          </p>
        </div>
      </div>
    </li>
  </ol>
</template>
