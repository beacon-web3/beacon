<script setup lang="ts">
const { t } = useI18n()
const localePath = useLocalePath()

const signalStats = computed(() => [
  {
    value: t('home.signal.stats.stake.value'),
    label: t('home.signal.stats.stake.label')
  },
  {
    value: t('home.signal.stats.support.value'),
    label: t('home.signal.stats.support.label')
  },
  {
    value: t('home.signal.stats.record.value'),
    label: t('home.signal.stats.record.label')
  }
])

const reasons = computed(() => [
  {
    title: t('home.reasons.items.early.title'),
    description: t('home.reasons.items.early.description')
  },
  {
    title: t('home.reasons.items.public.title'),
    description: t('home.reasons.items.public.description')
  },
  {
    title: t('home.reasons.items.constrained.title'),
    description: t('home.reasons.items.constrained.description')
  }
])

const steps = computed(() => [
  {
    number: t('home.how.steps.recommend.number'),
    title: t('home.how.steps.recommend.title'),
    description: t('home.how.steps.recommend.description')
  },
  {
    number: t('home.how.steps.support.number'),
    title: t('home.how.steps.support.title'),
    description: t('home.how.steps.support.description')
  },
  {
    number: t('home.how.steps.reputation.number'),
    title: t('home.how.steps.reputation.title'),
    description: t('home.how.steps.reputation.description')
  }
])

const ledgerRows = computed(() => [
  {
    label: t('home.ledger.rows.action.label'),
    value: t('home.ledger.rows.action.value'),
    note: t('home.ledger.rows.action.note')
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
    <section class="beacon-container grid min-h-[calc(100vh-4rem)] gap-12 py-16 sm:py-24 lg:grid-cols-[minmax(0,0.95fr)_minmax(22rem,0.72fr)] lg:items-center">
      <div>
        <UBadge
          :label="t('home.badge')"
          color="primary"
          variant="subtle"
          size="lg"
        />

        <h1 class="beacon-display mt-8 max-w-4xl text-6xl text-ink sm:text-7xl lg:text-8xl">
          {{ t('home.title') }}
        </h1>

        <p class="mt-8 max-w-2xl text-lg leading-8 text-ink-muted sm:text-xl sm:leading-9">
          {{ t('home.description') }}
        </p>

        <div class="mt-10 flex flex-col gap-3 sm:flex-row">
          <UButton
            :to="localePath('/signup')"
            size="xl"
            :label="t('home.primaryCta')"
            trailing-icon="i-lucide-arrow-right"
            class="justify-center"
          />
          <UButton
            :to="`${localePath('/')}#signal`"
            size="xl"
            :label="t('home.secondaryCta')"
            color="neutral"
            variant="ghost"
            class="justify-center"
          />
        </div>
      </div>

      <aside
        id="signal"
        class="beacon-panel p-5 sm:p-6"
        :aria-label="t('home.signal.ariaLabel')"
      >
        <div class="flex items-center justify-between gap-4 border-b border-rule pb-5">
          <div>
            <p class="beacon-kicker">
              {{ t('home.signal.eyebrow') }}
            </p>
            <h2 class="mt-2 text-2xl font-semibold tracking-[-0.04em] text-ink">
              {{ t('home.signal.title') }}
            </h2>
          </div>
          <UIcon
            name="i-lucide-book-open-check"
            class="size-6 shrink-0 text-beacon-600 dark:text-beacon-300"
          />
        </div>

        <blockquote class="mt-6 text-2xl font-medium leading-9 tracking-[-0.04em] text-ink sm:text-3xl sm:leading-10">
          {{ t('home.signal.thesis') }}
        </blockquote>

        <p class="mt-4 text-sm font-medium leading-6 text-ink-muted">
          {{ t('home.signal.meta') }}
        </p>

        <dl class="mt-8 grid gap-3">
          <div
            v-for="stat in signalStats"
            :key="stat.label"
            class="grid grid-cols-[minmax(0,1fr)_auto] items-baseline gap-4 border-t border-rule pt-3"
          >
            <dt class="text-xs font-semibold uppercase tracking-[0.14em] text-ink-faint">
              {{ stat.label }}
            </dt>
            <dd class="text-sm font-semibold text-ink">
              {{ stat.value }}
            </dd>
          </div>
        </dl>
      </aside>
    </section>

    <section class="beacon-container border-t border-rule py-16 sm:py-20">
      <div class="grid gap-8 lg:grid-cols-[minmax(0,0.7fr)_minmax(0,1fr)] lg:items-start">
        <div>
          <p class="beacon-kicker">
            {{ t('home.reasons.eyebrow') }}
          </p>
          <h2 class="mt-4 max-w-xl text-4xl font-semibold tracking-[-0.055em] text-ink sm:text-5xl">
            {{ t('home.reasons.title') }}
          </h2>
        </div>

        <div class="grid gap-4 sm:grid-cols-3 lg:gap-6">
          <article
            v-for="reason in reasons"
            :key="reason.title"
            class="border-t border-rule pt-5"
          >
            <h3 class="text-lg font-semibold tracking-[-0.03em] text-ink">
              {{ reason.title }}
            </h3>
            <p class="mt-3 text-sm leading-7 text-ink-muted">
              {{ reason.description }}
            </p>
          </article>
        </div>
      </div>
    </section>

    <section
      id="how-it-works"
      class="border-y border-rule bg-paper/58 py-16 sm:py-20"
    >
      <div class="beacon-container">
        <div class="max-w-3xl">
          <p class="beacon-kicker">
            {{ t('home.how.eyebrow') }}
          </p>
          <h2 class="mt-4 text-4xl font-semibold tracking-[-0.055em] text-ink sm:text-5xl">
            {{ t('home.how.title') }}
          </h2>
          <p class="mt-5 text-base leading-8 text-ink-muted">
            {{ t('home.how.description') }}
          </p>
        </div>

        <div class="mt-12 grid gap-5 md:grid-cols-3">
          <article
            v-for="step in steps"
            :key="step.number"
            class="rounded-xl border border-rule bg-canvas p-5"
          >
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-beacon-700 dark:text-beacon-300">
              {{ step.number }}
            </p>
            <h3 class="mt-6 text-xl font-semibold tracking-[-0.04em] text-ink">
              {{ step.title }}
            </h3>
            <p class="mt-3 text-sm leading-7 text-ink-muted">
              {{ step.description }}
            </p>
          </article>
        </div>
      </div>
    </section>

    <section
      id="ledger"
      class="beacon-container grid gap-10 py-16 sm:py-24 lg:grid-cols-[minmax(0,0.78fr)_minmax(20rem,0.62fr)] lg:items-start"
    >
      <div>
        <p class="beacon-kicker">
          {{ t('home.ledger.eyebrow') }}
        </p>
        <h2 class="mt-4 max-w-2xl text-4xl font-semibold tracking-[-0.055em] text-ink sm:text-5xl">
          {{ t('home.ledger.title') }}
        </h2>
        <p class="mt-5 max-w-2xl text-base leading-8 text-ink-muted">
          {{ t('home.ledger.description') }}
        </p>
        <p class="mt-6 max-w-2xl text-sm leading-7 text-ink-faint">
          {{ t('home.ledger.notice') }}
        </p>
      </div>

      <BeaconLedgerPreview
        :eyebrow="t('home.ledger.previewEyebrow')"
        :title="t('home.ledger.previewTitle')"
        :description="t('home.ledger.previewDescription')"
        :rows="ledgerRows"
      />
    </section>

    <section class="beacon-container pb-16 sm:pb-24">
      <div class="rounded-2xl border border-rule bg-ink p-7 text-paper sm:p-10 lg:flex lg:items-end lg:justify-between lg:gap-10">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.16em] text-paper/70">
            {{ t('home.final.eyebrow') }}
          </p>
          <h2 class="mt-4 max-w-2xl text-4xl font-semibold tracking-[-0.055em] sm:text-5xl">
            {{ t('home.final.title') }}
          </h2>
        </div>
        <UButton
          :to="localePath('/signup')"
          size="xl"
          :label="t('home.final.cta')"
          color="primary"
          trailing-icon="i-lucide-arrow-right"
          class="mt-8 justify-center lg:mt-0"
        />
      </div>
    </section>
  </div>
</template>
