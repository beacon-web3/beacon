<script setup lang="ts">
defineProps<{
  number: string
  title: string
  description: string
}>()
</script>

<template>
  <article class="relative rounded-xl border border-rule bg-paper/78 p-6 shadow-ledger">
    <div class="flex items-start gap-4">
      <span class="grid size-10 shrink-0 place-items-center rounded-full border border-ledger-line bg-ledger-50 font-serif text-lg font-semibold text-ledger-700 dark:bg-ledger-900 dark:text-ledger-100">
        {{ number }}
      </span>
      <div>
        <h3 class="text-xl font-semibold tracking-[-0.03em] text-ink">
          {{ title }}
        </h3>
        <p class="mt-3 text-sm leading-7 text-ink-muted">
          {{ description }}
        </p>
      </div>
    </div>
  </article>
</template>
