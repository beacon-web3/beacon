<script setup lang="ts">
const { t } = useI18n()
const localePath = useLocalePath()

const metrics = computed(() => [
  {
    value: t('home.metrics.problem.value'),
    label: t('home.metrics.problem.label')
  },
  {
    value: t('home.metrics.mechanism.value'),
    label: t('home.metrics.mechanism.label')
  },
  {
    value: t('home.metrics.outcome.value'),
    label: t('home.metrics.outcome.label')
  }
])

const problems = computed(() => [
  {
    icon: 'i-lucide-radio-tower',
    title: t('home.problem.items.feeds.title'),
    description: t('home.problem.items.feeds.description')
  },
  {
    icon: 'i-lucide-star-half',
    title: t('home.problem.items.reviews.title'),
    description: t('home.problem.items.reviews.description')
  },
  {
    icon: 'i-lucide-sparkles',
    title: t('home.problem.items.ai.title'),
    description: t('home.problem.items.ai.description')
  }
])

const solutionPoints = computed(() => [
  t('home.solution.points.canonical'),
  t('home.solution.points.stake'),
  t('home.solution.points.support'),
  t('home.solution.points.ledger')
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
  },
  {
    number: t('home.how.steps.governance.number'),
    title: t('home.how.steps.governance.title'),
    description: t('home.how.steps.governance.description')
  }
])

const roadmapPhases = computed(() => [
  {
    phase: t('home.roadmap.phases.phase0.phase'),
    title: t('home.roadmap.phases.phase0.title'),
    description: t('home.roadmap.phases.phase0.description')
  },
  {
    phase: t('home.roadmap.phases.phase1.phase'),
    title: t('home.roadmap.phases.phase1.title'),
    description: t('home.roadmap.phases.phase1.description')
  },
  {
    phase: t('home.roadmap.phases.phase2.phase'),
    title: t('home.roadmap.phases.phase2.title'),
    description: t('home.roadmap.phases.phase2.description')
  },
  {
    phase: t('home.roadmap.phases.phase3.phase'),
    title: t('home.roadmap.phases.phase3.title'),
    description: t('home.roadmap.phases.phase3.description')
  },
  {
    phase: t('home.roadmap.phases.phase4.phase'),
    title: t('home.roadmap.phases.phase4.title'),
    description: t('home.roadmap.phases.phase4.description')
  },
  {
    phase: t('home.roadmap.phases.phase5.phase'),
    title: t('home.roadmap.phases.phase5.title'),
    description: t('home.roadmap.phases.phase5.description')
  },
  {
    phase: t('home.roadmap.phases.phase6.phase'),
    title: t('home.roadmap.phases.phase6.title'),
    description: t('home.roadmap.phases.phase6.description')
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

        <h1 class="beacon-editorial-title mt-7 max-w-4xl text-5xl text-ink sm:text-7xl lg:text-8xl">
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
            :to="`${localePath('/')}#how-it-works`"
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
        :recommendation-label="t('home.book.recommendationLabel')"
        :title="t('home.book.title')"
        :author="t('home.book.author')"
        :thesis="t('home.book.thesis')"
        :curator-label="t('home.book.curatorLabel')"
        :curator="t('home.book.curator')"
        :reputation-label="t('home.book.reputationLabel')"
        :reputation="t('home.book.reputation')"
        :supporters-label="t('home.book.supportersLabel')"
        :supporters="t('home.book.supporters')"
      />
    </section>

    <section
      id="problem"
      class="border-y border-rule bg-paper/62 py-16 sm:py-20"
    >
      <div class="beacon-container">
        <div class="max-w-3xl">
          <p class="beacon-kicker">
            {{ t('home.problem.eyebrow') }}
          </p>
          <h2 class="mt-3 font-serif text-4xl font-semibold tracking-[-0.045em] text-ink sm:text-5xl">
            {{ t('home.problem.title') }}
          </h2>
          <p class="mt-5 text-base leading-8 text-ink-muted">
            {{ t('home.problem.description') }}
          </p>
        </div>

        <div class="mt-10 grid gap-4 md:grid-cols-3">
          <BeaconProblemCard
            v-for="problem in problems"
            :key="problem.title"
            :icon="problem.icon"
            :title="problem.title"
            :description="problem.description"
          />
        </div>
      </div>
    </section>

    <section class="beacon-container grid gap-10 py-16 sm:py-24 lg:grid-cols-[minmax(0,0.75fr)_minmax(0,0.85fr)] lg:items-start">
      <div>
        <p class="beacon-kicker">
          {{ t('home.solution.eyebrow') }}
        </p>
        <h2 class="mt-3 font-serif text-4xl font-semibold tracking-[-0.045em] text-ink sm:text-5xl">
          {{ t('home.solution.title') }}
        </h2>
        <p class="mt-5 text-base leading-8 text-ink-muted">
          {{ t('home.solution.description') }}
        </p>
      </div>

      <ul class="grid gap-3">
        <li
          v-for="point in solutionPoints"
          :key="point"
          class="flex gap-3 rounded-xl border border-rule bg-vellum/70 p-5 text-sm leading-7 text-ink-muted"
        >
          <UIcon
            name="i-lucide-check-circle-2"
            class="mt-1 size-5 shrink-0 text-beacon-700 dark:text-beacon-200"
          />
          <span>{{ point }}</span>
        </li>
      </ul>
    </section>

    <section
      id="how-it-works"
      class="border-y border-rule bg-paper/62 py-16 sm:py-20"
    >
      <div class="beacon-container">
        <div class="max-w-3xl">
          <p class="beacon-kicker">
            {{ t('home.how.eyebrow') }}
          </p>
          <h2 class="mt-3 font-serif text-4xl font-semibold tracking-[-0.045em] text-ink sm:text-5xl">
            {{ t('home.how.title') }}
          </h2>
          <p class="mt-5 text-base leading-8 text-ink-muted">
            {{ t('home.how.description') }}
          </p>
        </div>

        <div class="mt-10 grid gap-4 lg:grid-cols-2">
          <BeaconHowItWorksStep
            v-for="step in steps"
            :key="step.number"
            :number="step.number"
            :title="step.title"
            :description="step.description"
          />
        </div>
      </div>
    </section>

    <section class="beacon-container py-16 sm:py-24">
      <div class="beacon-panel overflow-hidden">
        <div class="grid gap-0 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,0.7fr)]">
          <div class="p-7 sm:p-10">
            <p class="beacon-kicker">
              {{ t('home.vision.eyebrow') }}
            </p>
            <h2 class="mt-3 font-serif text-4xl font-semibold tracking-[-0.045em] text-ink sm:text-5xl">
              {{ t('home.vision.title') }}
            </h2>
            <p class="mt-5 text-base leading-8 text-ink-muted">
              {{ t('home.vision.description') }}
            </p>
          </div>

          <div class="border-t border-rule bg-vellum/70 p-7 sm:p-10 lg:border-s lg:border-t-0">
            <div class="flex gap-3">
              <UIcon
                name="i-lucide-shield-check"
                class="mt-1 size-5 shrink-0 text-beacon-700 dark:text-beacon-200"
              />
              <p class="text-sm leading-7 text-ink-muted">
                {{ t('home.vision.notice') }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section
      id="roadmap"
      class="border-y border-rule bg-paper/62 py-16 sm:py-20"
    >
      <div class="beacon-container grid gap-10 lg:grid-cols-[minmax(0,0.66fr)_minmax(0,0.9fr)] lg:items-start">
        <div class="lg:sticky lg:top-24">
          <p class="beacon-kicker">
            {{ t('home.roadmap.eyebrow') }}
          </p>
          <h2 class="mt-3 font-serif text-4xl font-semibold tracking-[-0.045em] text-ink sm:text-5xl">
            {{ t('home.roadmap.title') }}
          </h2>
          <p class="mt-5 text-base leading-8 text-ink-muted">
            {{ t('home.roadmap.description') }}
          </p>
        </div>

        <BeaconRoadmapTimeline :phases="roadmapPhases" />
      </div>
    </section>

    <section
      id="ledger"
      class="beacon-container grid gap-10 py-16 sm:py-24 lg:grid-cols-[minmax(0,0.85fr)_minmax(22rem,0.65fr)] lg:items-start"
    >
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
        :eyebrow="t('home.ledger.previewEyebrow')"
        :title="t('home.ledger.previewTitle')"
        :description="t('home.ledger.previewDescription')"
        :rows="ledgerRows"
      />
    </section>
  </div>
</template>
