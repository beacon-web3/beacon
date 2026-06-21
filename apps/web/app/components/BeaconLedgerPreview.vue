<script setup lang="ts">
defineProps<{
  title: string
  description: string
  rows: Array<{
    label: string
    value: string
    note?: string
  }>
}>()
</script>

<template>
  <aside class="beacon-panel p-6 sm:p-7">
    <div class="flex items-start gap-3">
      <div class="grid size-10 place-items-center rounded-md border border-ledger-line bg-ledger-50 text-ledger-700 dark:bg-ledger-900 dark:text-ledger-100">
        <UIcon
          name="i-lucide-receipt-text"
          class="size-5"
        />
      </div>
      <div>
        <p class="beacon-kicker">
          Ledger preview
        </p>
        <h2 class="mt-2 text-xl font-semibold tracking-[-0.03em] text-ink">
          {{ title }}
        </h2>
        <p class="mt-2 text-sm leading-6 text-ink-muted">
          {{ description }}
        </p>
      </div>
    </div>

    <dl class="mt-6">
      <div
        v-for="row in rows"
        :key="row.label"
        class="beacon-ledger-row"
      >
        <dt>
          <span class="block text-sm font-medium text-ink">{{ row.label }}</span>
          <span
            v-if="row.note"
            class="mt-1 block text-xs leading-5 text-ink-muted"
          >{{ row.note }}</span>
        </dt>
        <dd class="text-end text-sm font-semibold text-ink">
          {{ row.value }}
        </dd>
      </div>
    </dl>
  </aside>
</template>
