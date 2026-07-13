<script setup lang="ts">
definePageMeta({
  layout: 'default'
})

const { t } = useI18n()
const localePath = useLocalePath()
const route = useRoute()
const accountStore = useAccountStore()

await accountStore.fetchAccount()

const socialAuthSucceeded = computed(() => route.query.social_auth === 'success')
</script>

<template>
  <div class="beacon-container py-16 sm:py-24">
    <section class="beacon-panel p-5 sm:p-6">
      <div class="flex flex-col gap-5 border-b border-rule pb-6 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p class="beacon-kicker">
            {{ t('dashboard.eyebrow') }}
          </p>
          <h1 class="mt-3 max-w-2xl text-4xl font-semibold tracking-[-0.055em] text-ink sm:text-5xl">
            {{ t('dashboard.title') }}
          </h1>
          <p class="mt-4 max-w-2xl text-base leading-8 text-ink-muted">
            {{ t('dashboard.description') }}
          </p>
        </div>
        <UIcon
          name="i-lucide-user-round-check"
          class="size-8 shrink-0 text-beacon-600 dark:text-beacon-300"
        />
      </div>

      <div class="mt-6">
        <UAlert
          v-if="socialAuthSucceeded && accountStore.account"
          role="status"
          color="success"
          variant="soft"
          :title="t('dashboard.socialAuthSuccess')"
        />
        <UAlert
          v-else-if="accountStore.status === 'pending'"
          role="status"
          color="neutral"
          variant="soft"
          :title="t('dashboard.loading')"
        />
        <UAlert
          v-else-if="accountStore.error"
          role="alert"
          color="error"
          variant="soft"
          :title="t('dashboard.authRequired')"
        />
      </div>

      <dl
        v-if="accountStore.account"
        class="mt-8 grid gap-3 sm:grid-cols-2"
      >
        <div class="rounded-xl border border-rule bg-paper p-4">
          <dt class="text-xs font-semibold uppercase tracking-[0.14em] text-ink-faint">
            {{ t('dashboard.emailLabel') }}
          </dt>
          <dd class="mt-2 text-base font-semibold text-ink">
            {{ accountStore.account.email }}
          </dd>
        </div>
        <div class="rounded-xl border border-rule bg-paper p-4">
          <dt class="text-xs font-semibold uppercase tracking-[0.14em] text-ink-faint">
            {{ t('dashboard.usernameLabel') }}
          </dt>
          <dd class="mt-2 text-base font-semibold text-ink">
            {{ accountStore.account.username }}
          </dd>
        </div>
      </dl>

      <div
        v-if="accountStore.error"
        class="mt-6"
      >
        <UButton
          :to="localePath('/login')"
          :label="t('dashboard.loginLink')"
          trailing-icon="i-lucide-arrow-right"
        />
      </div>
    </section>
  </div>
</template>
