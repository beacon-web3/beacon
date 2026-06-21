<script setup lang="ts">
const { t } = useI18n()
const localePath = useLocalePath()

const metrics = computed(() => [
  {
    value: t('home.metrics.books.value'),
    label: t('home.metrics.books.label')
  },
  {
    value: t('home.metrics.curators.value'),
    label: t('home.metrics.curators.label')
  },
  {
    value: t('home.metrics.ledger.value'),
    label: t('home.metrics.ledger.label')
  }
])

const principles = computed(() => [
  {
    icon: 'i-lucide-book-open-check',
    title: t('home.principles.books.title'),
    description: t('home.principles.books.description')
  },
  {
    icon: 'i-lucide-fingerprint',
    title: t('home.principles.reputation.title'),
    description: t('home.principles.reputation.description')
  },
  {
    icon: 'i-lucide-receipt-text',
    title: t('home.principles.ledger.title'),
    description: t('home.principles.ledger.description')
  }
])

const ledgerRows = computed(() => [
  {
    label: t('home.ledger.rows.action.label'),
    value: t('home.ledger.rows.action.value'),
    note: t('home.ledger.rows.action.note')
  },
  {
    label: t('home.ledger.rows.recipient.label'),
    value: t('home.ledger.rows.recipient.value'),
    note: t('home.ledger.rows.recipient.note')
  },
  {
    label: t('home.ledger.rows.amount.label'),
    value: t('home.ledger.rows.amount.value'),
    note: t('home.ledger.rows.amount.note')
  },
  {
    label: t('home.ledger.rows.cluster.label'),
    value: t('home.ledger.rows.cluster.value'),
    note: t('home.ledger.rows.cluster.note')
  }
])
</script>

<template>
  <div>
    <section class="beacon-container grid gap-12 py-16 sm:py-24 lg:grid-cols-[minmax(0,0.92fr)_minmax(28rem,1.08fr)] lg:items-center">
      <div>
        <UBadge
          color="primary"
          variant="subtle"
          icon="i-lucide-library"
          :label="t('home.badge')"
        />

        <h1 class="beacon-editorial-title mt-7 max-w-4xl text-6xl text-ink sm:text-7xl lg:text-8xl">
          {{ t('home.title') }}
        </h1>

        <p class="mt-7 max-w-2xl text-lg leading-8 text-ink-muted">
          {{ t('home.description') }}
        </p>

        <div class="mt-9 flex flex-col gap-3 sm:flex-row">
          <UButton
            :to="localePath('/signup')"
            size="xl"
            :label="t('home.primaryCta')"
            trailing-icon="i-lucide-arrow-right"
            class="justify-center"
          />
          <UButton
            :to="localePath('/login')"
            size="xl"
            :label="t('home.secondaryCta')"
            color="neutral"
            variant="outline"
            class="justify-center"
          />
        </div>

        <dl class="mt-12 grid gap-3 sm:grid-cols-3">
          <div
            v-for="metric in metrics"
            :key="metric.label"
            class="rounded-lg border border-rule bg-paper/72 p-4"
          >
            <dt class="text-xs font-semibold uppercase tracking-[0.14em] text-ink-faint">
              {{ metric.label }}
            </dt>
            <dd class="mt-2 font-serif text-2xl font-semibold tracking-[-0.04em] text-ink">
              {{ metric.value }}
            </dd>
          </div>
        </dl>
      </div>

      <BeaconBookCard
        :eyebrow="t('home.book.eyebrow')"
        :title="t('home.book.title')"
        :author="t('home.book.author')"
        :thesis="t('home.book.thesis')"
        :curator="t('home.book.curator')"
        :reputation="t('home.book.reputation')"
        :supporters="t('home.book.supporters')"
      />
    </section>

    <section class="border-y border-rule bg-paper/62 py-16 sm:py-20">
      <div class="beacon-container">
        <div class="max-w-3xl">
          <p class="beacon-kicker">
            {{ t('home.principles.eyebrow') }}
          </p>
          <h2 class="mt-3 font-serif text-4xl font-semibold tracking-[-0.045em] text-ink sm:text-5xl">
            {{ t('home.principles.title') }}
          </h2>
          <p class="mt-4 text-base leading-8 text-ink-muted">
            {{ t('home.principles.description') }}
          </p>
        </div>

        <div class="mt-10 grid gap-4 md:grid-cols-3">
          <BeaconPrincipleCard
            v-for="principle in principles"
            :key="principle.title"
            :icon="principle.icon"
            :title="principle.title"
            :description="principle.description"
          />
        </div>
      </div>
    </section>

    <section class="beacon-container grid gap-10 py-16 sm:py-24 lg:grid-cols-[minmax(0,0.85fr)_minmax(22rem,0.65fr)] lg:items-start">
      <div>
        <p class="beacon-kicker">
          {{ t('home.ledger.eyebrow') }}
        </p>
        <h2 class="mt-3 font-serif text-4xl font-semibold tracking-[-0.045em] text-ink sm:text-5xl">
          {{ t('home.ledger.title') }}
        </h2>
        <p class="mt-5 max-w-2xl text-base leading-8 text-ink-muted">
          {{ t('home.ledger.description') }}
        </p>

        <div class="mt-8 rounded-xl border border-rule bg-vellum/70 p-5">
          <div class="flex gap-3">
            <UIcon
              name="i-lucide-shield-check"
              class="mt-1 size-5 shrink-0 text-beacon-700 dark:text-beacon-200"
            />
            <p class="text-sm leading-7 text-ink-muted">
              {{ t('home.ledger.notice') }}
            </p>
          </div>
        </div>
      </div>

      <BeaconLedgerPreview
        :title="t('home.ledger.previewTitle')"
        :description="t('home.ledger.previewDescription')"
        :rows="ledgerRows"
      />
    </section>
  </div>
</template>
