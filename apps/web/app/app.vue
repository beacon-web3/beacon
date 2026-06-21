<script setup lang="ts">
const { t, locale, localeProperties } = useI18n()
const localePath = useLocalePath()

const navLinks = computed(() => [
  { label: t('nav.discover'), to: localePath('/') },
  { label: t('nav.reputation'), to: localePath('/') },
  { label: t('nav.treasury'), to: localePath('/') }
])

const htmlLang = computed(() => String(localeProperties.value.iso || locale.value || 'en'))
const htmlDir = computed(() => {
  const dir = localeProperties.value.dir

  return dir === 'rtl' || dir === 'auto' ? dir : 'ltr'
})

useHead(() => ({
  meta: [{ name: 'viewport', content: 'width=device-width, initial-scale=1' }],
  link: [{ rel: 'icon', href: '/favicon.ico' }],
  htmlAttrs: {
    lang: htmlLang.value,
    dir: htmlDir.value
  }
}))

useSeoMeta({
  title: () => t('seo.title'),
  description: () => t('seo.description'),
  ogTitle: () => t('seo.title'),
  ogDescription: () => t('seo.description'),
  twitterCard: 'summary_large_image'
})
</script>

<template>
  <UApp>
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

    <UMain class="min-h-[calc(100vh-9rem)]">
      <NuxtPage />
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
  </UApp>
</template>
