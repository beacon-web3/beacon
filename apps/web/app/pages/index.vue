<script setup lang="ts">
const { t } = useI18n()
const localePath = useLocalePath()

const stats = computed(() => [
  {
    value: t('home.stats.stake.value'),
    label: t('home.stats.stake.label')
  },
  {
    value: t('home.stats.support.value'),
    label: t('home.stats.support.label')
  },
  {
    value: t('home.stats.period.value'),
    label: t('home.stats.period.label')
  }
])

const steps = computed(() => [
  {
    icon: 'i-lucide-book-open-check',
    title: t('home.steps.recommend.title'),
    description: t('home.steps.recommend.description')
  },
  {
    icon: 'i-lucide-hand-coins',
    title: t('home.steps.support.title'),
    description: t('home.steps.support.description')
  },
  {
    icon: 'i-lucide-trophy',
    title: t('home.steps.earn.title'),
    description: t('home.steps.earn.description')
  }
])

const ctaLinks = computed(() => [
  {
    label: t('home.cta.primary'),
    to: localePath('/signup'),
    trailingIcon: 'i-lucide-arrow-right'
  },
  {
    label: t('home.cta.secondary'),
    to: localePath('/login'),
    color: 'neutral' as const,
    variant: 'outline' as const
  }
])
</script>

<template>
  <div class="overflow-hidden">
    <section class="relative isolate px-6 py-20 sm:py-28 lg:px-8">
      <div
        class="absolute inset-x-0 top-0 -z-10 h-[36rem] bg-[radial-gradient(circle_at_top,#00dc8240,transparent_55%)]"
      />

      <div
        class="mx-auto grid max-w-7xl items-center gap-14 lg:grid-cols-[1.05fr_0.95fr]"
      >
        <div>
          <UBadge
            color="primary"
            variant="subtle"
            icon="i-lucide-radar"
            :label="t('home.badge')"
            class="mb-6"
          />

          <h1
            class="max-w-4xl text-5xl font-black tracking-tight text-neutral-950 sm:text-7xl dark:text-white"
          >
            {{ t('home.title') }}
          </h1>

          <p
            class="mt-6 max-w-2xl text-lg leading-8 text-neutral-600 dark:text-neutral-300"
          >
            {{ t('home.description') }}
          </p>

          <div class="mt-8">
            <p class="text-lg font-semibold text-primary">
              {{ t('home.principle') }}
            </p>
            <p class="mt-1 text-base text-neutral-600 dark:text-neutral-400">
              {{ t('home.tagline') }}
            </p>
          </div>

          <div class="mt-10 flex flex-col gap-3 sm:flex-row">
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

          <div class="mt-12 grid gap-4 sm:grid-cols-3">
            <div
              v-for="stat in stats"
              :key="stat.value"
              class="rounded-2xl border border-neutral-200/70 bg-white/70 p-4 shadow-sm backdrop-blur dark:border-white/10 dark:bg-white/5"
            >
              <p class="font-bold text-neutral-950 dark:text-white">
                {{ stat.value }}
              </p>
              <p class="mt-1 text-sm text-neutral-600 dark:text-neutral-400">
                {{ stat.label }}
              </p>
            </div>
          </div>
        </div>

        <div class="relative">
          <div
            class="absolute -inset-6 -z-10 rounded-[3rem] bg-primary/15 blur-3xl"
          />
          <div
            class="rounded-[2rem] border border-neutral-200 bg-white p-6 shadow-2xl dark:border-white/10 dark:bg-neutral-950"
          >
            <div
              class="flex items-center justify-between border-b border-neutral-200 pb-5 dark:border-white/10"
            >
              <div>
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  {{ t('home.signalCard.eyebrow') }}
                </p>
                <h2
                  class="mt-1 text-xl font-black text-neutral-950 dark:text-white"
                >
                  {{ t('home.signalCard.title') }}
                </h2>
              </div>
              <UIcon
                name="i-lucide-sparkles"
                class="size-8 text-primary"
              />
            </div>

            <div class="mt-6 space-y-4">
              <div class="rounded-2xl bg-neutral-100 p-5 dark:bg-white/5">
                <div class="flex items-start justify-between gap-4">
                  <div>
                    <p class="text-sm font-semibold text-primary">
                      {{ t('home.signalCard.commitmentLabel') }}
                    </p>
                    <p
                      class="mt-1 text-3xl font-black text-neutral-950 dark:text-white"
                    >
                      {{ t('home.signalCard.commitmentValue') }}
                    </p>
                  </div>
                  <UBadge
                    color="primary"
                    variant="soft"
                    :label="t('home.signalCard.badge')"
                  />
                </div>
                <p
                  class="mt-4 text-sm leading-6 text-neutral-600 dark:text-neutral-300"
                >
                  {{ t('home.signalCard.description') }}
                </p>
              </div>

              <div class="grid gap-3 sm:grid-cols-2">
                <div
                  class="rounded-2xl border border-neutral-200 p-4 dark:border-white/10"
                >
                  <p class="text-sm text-neutral-500 dark:text-neutral-400">
                    {{ t('home.signalCard.supportersLabel') }}
                  </p>
                  <p
                    class="mt-1 text-2xl font-black text-neutral-950 dark:text-white"
                  >
                    {{ t('home.signalCard.supportersValue') }}
                  </p>
                </div>
                <div
                  class="rounded-2xl border border-neutral-200 p-4 dark:border-white/10"
                >
                  <p class="text-sm text-neutral-500 dark:text-neutral-400">
                    {{ t('home.signalCard.scoreLabel') }}
                  </p>
                  <p
                    class="mt-1 text-2xl font-black text-neutral-950 dark:text-white"
                  >
                    {{ t('home.signalCard.scoreValue') }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <UPageSection
      :title="t('home.stepsSection.title')"
      :description="t('home.stepsSection.description')"
    >
      <div class="grid gap-6 md:grid-cols-3">
        <UCard
          v-for="step in steps"
          :key="step.title"
          class="h-full"
        >
          <UIcon
            :name="step.icon"
            class="mb-5 size-8 text-primary"
          />
          <h3 class="text-xl font-black text-neutral-950 dark:text-white">
            {{ step.title }}
          </h3>
          <p class="mt-3 leading-7 text-neutral-600 dark:text-neutral-300">
            {{ step.description }}
          </p>
        </UCard>
      </div>
    </UPageSection>

    <UPageSection>
      <UPageCTA
        :title="t('home.cta.title')"
        :description="t('home.cta.description')"
        variant="subtle"
        :links="ctaLinks"
      />
    </UPageSection>
  </div>
</template>
