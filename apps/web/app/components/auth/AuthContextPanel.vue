<script setup lang="ts">
defineProps<{
  title: string
  description: string
}>()

const { t } = useI18n()
</script>

<template>
  <div>
    <UBadge
      :label="t('auth.badge')"
      color="primary"
      variant="subtle"
      size="lg"
    />

    <h1 class="beacon-display mt-8 max-w-3xl text-5xl text-ink sm:text-6xl lg:text-7xl">
      {{ t(title) }}
    </h1>

    <p class="mt-7 max-w-2xl text-lg leading-8 text-ink-muted">
      {{ t(description) }}
    </p>

    <div class="mt-10 grid max-w-2xl gap-4 sm:grid-cols-3">
      <div class="border-t border-rule pt-4">
        <p class="text-xs font-semibold uppercase tracking-[0.16em] text-ink-faint">
          {{ t('auth.context.bookFirst.label') }}
        </p>
        <p class="mt-2 text-sm font-semibold text-ink">
          {{ t('auth.context.bookFirst.value') }}
        </p>
      </div>
      <div class="border-t border-rule pt-4">
        <p class="text-xs font-semibold uppercase tracking-[0.16em] text-ink-faint">
          {{ t('auth.context.wallet.label') }}
        </p>
        <p class="mt-2 text-sm font-semibold text-ink">
          {{ t('auth.context.wallet.value') }}
        </p>
      </div>
      <div class="border-t border-rule pt-4">
        <p class="text-xs font-semibold uppercase tracking-[0.16em] text-ink-faint">
          {{ t('auth.context.status.label') }}
        </p>
        <p class="mt-2 text-sm font-semibold text-ink">
          {{ t('auth.context.status.value') }}
        </p>
      </div>
    </div>
  </div>
</template>
