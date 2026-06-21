<script setup lang="ts">
defineProps<{
  eyebrow: string
  title: string
  author: string
  thesis: string
  curator: string
  reputation: string
  supporters: string
}>()
</script>

<template>
  <article class="beacon-panel overflow-hidden">
    <div class="grid gap-0 sm:grid-cols-[12rem_minmax(0,1fr)]">
      <div class="border-b border-rule bg-vellum p-5 sm:border-b-0 sm:border-e">
        <div class="aspect-[3/4] rounded-lg border border-rule bg-paper p-4 shadow-ledger">
          <div class="flex h-full flex-col justify-between border border-rule p-4">
            <p class="beacon-kicker text-[0.62rem]">
              {{ eyebrow }}
            </p>
            <div>
              <h3 class="font-serif text-3xl font-semibold leading-none tracking-[-0.04em] text-ink">
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
        <p class="beacon-kicker">
          Canonical recommendation
        </p>
        <blockquote class="mt-4 font-serif text-2xl leading-8 tracking-[-0.03em] text-ink sm:text-3xl sm:leading-10">
          {{ thesis }}
        </blockquote>

        <dl class="mt-7 grid gap-4 border-t border-rule pt-5 sm:grid-cols-3">
          <div>
            <dt class="text-xs font-semibold uppercase tracking-[0.14em] text-ink-faint">
              Curator
            </dt>
            <dd class="mt-1 font-semibold text-ink">
              {{ curator }}
            </dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-[0.14em] text-ink-faint">
              Reputation
            </dt>
            <dd class="mt-1 font-semibold text-reputation">
              {{ reputation }}
            </dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-[0.14em] text-ink-faint">
              Supporters
            </dt>
            <dd class="mt-1 font-semibold text-ink">
              {{ supporters }}
            </dd>
          </div>
        </dl>
      </div>
    </div>
  </article>
</template>
