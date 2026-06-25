<script setup lang="ts">
const { t } = useI18n()
const localePath = useLocalePath()

const homeSectionPath = (hash: string) => `${localePath('/')}${hash}`

const navLinks = computed(() => [
  { label: t('nav.problem'), to: homeSectionPath('#signal') },
  { label: t('nav.howItWorks'), to: homeSectionPath('#how-it-works') },
  { label: t('nav.ledger'), to: homeSectionPath('#ledger') }
])
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
  </UHeader>

  <UMain>
    <slot />
  </UMain>

  <USeparator
    icon="i-lucide-book-open"
    class="text-ink-faint"
  />

  <UFooter
    :ui="{ container: 'pb-8' }"
  >
    <template #default>
      <p class="max-w-xl text-sm leading-6 text-ink-muted">
        {{ t('footer.description') }}
      </p>
    </template>
  </UFooter>
</template>
