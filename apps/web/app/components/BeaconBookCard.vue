<script setup lang="ts">
defineProps<{
  eyebrow: string
  title: string
  author: string
  thesis: string
  curator: string
  reputation: string
  supporters: string
  stake: string
  network: string
  milestone: string
  recommendationLabel: string
  curatorLabel: string
  reputationLabel: string
  supportersLabel: string
  stakeLabel: string
  networkLabel: string
  milestoneLabel: string
}>()
</script>

<template>
  <article class="beacon-panel overflow-hidden lg:-rotate-1">
    <div class="grid gap-0 sm:grid-cols-[13rem_minmax(0,1fr)]">
      <div class="border-b border-rule bg-vellum p-5 sm:border-b-0 sm:border-e">
        <div class="aspect-[3/4] rounded-lg border border-rule bg-paper p-4 shadow-ledger">
          <div class="flex h-full flex-col justify-between border border-rule p-4">
            <p class="beacon-kicker text-[0.62rem]">
              {{ eyebrow }}
            </p>
            <div>
              <h3 class="max-w-32 text-balance font-serif text-2xl font-semibold leading-[0.98] tracking-[-0.04em] text-ink sm:text-[1.7rem]">
                {{ title }}
              </h3>
              <p class="mt-3 text-sm font-medium text-ink-muted">
                {{ author }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div class="p-6 sm:p-7">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <p class="beacon-kicker">
            {{ recommendationLabel }}
          </p>
          <span class="inline-flex w-fit items-center gap-2 rounded-full border border-ledger-line bg-ledger-50 px-3 py-1 text-xs font-semibold text-ledger-700 dark:bg-ledger-900 dark:text-ledger-100">
            <UIcon
              name="i-lucide-radio"
              class="size-3.5"
            />
            {{ network }}
          </span>
        </div>

        <blockquote class="mt-4 font-serif text-2xl leading-8 tracking-[-0.03em] text-ink sm:text-[2rem] sm:leading-10">
          {{ thesis }}
        </blockquote>

        <dl class="mt-7 grid gap-4 border-t border-rule pt-5 sm:grid-cols-3">
          <div>
            <dt class="text-xs font-semibold uppercase tracking-[0.14em] text-ink-faint">
              {{ curatorLabel }}
            </dt>
            <dd class="mt-1 font-semibold text-ink">
              {{ curator }}
            </dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-[0.14em] text-ink-faint">
              {{ reputationLabel }}
            </dt>
            <dd class="mt-1 font-semibold text-reputation">
              {{ reputation }}
            </dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-[0.14em] text-ink-faint">
              {{ supportersLabel }}
            </dt>
            <dd class="mt-1 font-semibold text-ink">
              {{ supporters }}
            </dd>
          </div>
        </dl>

        <dl class="mt-5 grid gap-3 rounded-xl border border-rule bg-vellum/70 p-4 sm:grid-cols-3">
          <div>
            <dt class="text-xs font-semibold uppercase tracking-[0.14em] text-ink-faint">
              {{ stakeLabel }}
            </dt>
            <dd class="mt-1 text-sm font-semibold text-ink">
              {{ stake }}
            </dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-[0.14em] text-ink-faint">
              {{ networkLabel }}
            </dt>
            <dd class="mt-1 text-sm font-semibold text-ink">
              {{ network }}
            </dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-[0.14em] text-ink-faint">
              {{ milestoneLabel }}
            </dt>
            <dd class="mt-1 text-sm font-semibold text-ink">
              {{ milestone }}
            </dd>
          </div>
        </dl>
      </div>
    </div>
  </article>
</template>
