<script setup lang="ts">
const { t } = useI18n()
const localePath = useLocalePath()
const accountStore = useAccountStore()

const homeSectionPath = (hash: string) => `${localePath('/')}${hash}`

const navLinks = computed(() => [
  { label: t('nav.problem'), to: homeSectionPath('#signal') },
  { label: t('nav.howItWorks'), to: homeSectionPath('#how-it-works') },
  { label: t('nav.ledger'), to: homeSectionPath('#ledger') }
])

async function handleLogout() {
  await accountStore.logout()
}

onMounted(() => {
  if (accountStore.status !== 'success') {
    accountStore.fetchAccount()
  }
})
</script>

<template>
  <UHeader
    class="border-b border-rule/80 bg-paper/86 backdrop-blur-xl"
    :ui="{
      container: 'beacon-container h-16',
      left: 'min-w-0',
      center: 'hidden md:flex',
      right: 'gap-2'
    }"
  >
    <template #left>
      <NuxtLink
        :to="localePath('/')"
        :aria-label="t('nav.home')"
      >
        <AppLogo class="shrink-0" />
      </NuxtLink>
    </template>

    <UNavigationMenu
      :items="navLinks"
      variant="link"
      color="neutral"
      class="justify-center"
    />

    <template #right>
      <LanguageSwitcher />

      <UColorModeButton
        color="neutral"
        variant="ghost"
      />

      <template v-if="accountStore.isLoggedIn">
        <UButton
          :to="localePath('/dashboard')"
          :label="t('nav.dashboard')"
          color="neutral"
          variant="ghost"
        />

        <span class="text-sm font-medium text-ink-muted max-w-[10rem] truncate">
          {{ accountStore.account?.username }}
        </span>

        <UButton
          :label="t('nav.logout')"
          color="neutral"
          variant="ghost"
          @click="handleLogout"
        />
      </template>

      <template v-else>
        <UButton
          :to="localePath('/login')"
          :label="t('nav.login')"
          color="neutral"
          variant="ghost"
        />

        <UButton
          :to="localePath('/signup')"
          :label="t('nav.signup')"
          color="primary"
          trailing-icon="i-lucide-arrow-right"
          class="hidden sm:inline-flex"
        />
      </template>
    </template>
  </UHeader>

  <UMain class="min-h-[calc(100vh-9rem)]">
    <slot />
  </UMain>

  <USeparator
    icon="i-lucide-book-open"
    class="text-ink-faint"
  />

  <UFooter
    class="bg-paper/70"
    :ui="{ container: 'beacon-container py-8' }"
  >
    <template #left>
      <p class="max-w-xl text-sm leading-6 text-ink-muted">
        {{ t('footer.description') }}
      </p>
    </template>

    <template #right>
      <UButton
        :to="localePath('/signup')"
        :label="t('nav.joinWaitlist')"
        color="neutral"
        variant="outline"
      />
    </template>
  </UFooter>
</template>
