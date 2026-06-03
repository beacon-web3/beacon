<script setup>
const { t, locale, localeProperties } = useI18n()
const localePath = useLocalePath()

useHead(() => ({
  meta: [{ name: 'viewport', content: 'width=device-width, initial-scale=1' }],
  link: [{ rel: 'icon', href: '/favicon.ico' }],
  htmlAttrs: {
    lang: localeProperties.value.iso ?? locale.value,
    dir: localeProperties.value.dir ?? 'ltr'
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
    <UHeader>
      <template #left>
        <NuxtLink :to="localePath('/')">
          <AppLogo class="shrink-0" />
        </NuxtLink>
      </template>

      <template #right>
        <LanguageSwitcher />

        <UColorModeButton />

        <UButton
          :to="localePath('/login')"
          :label="t('nav.login')"
          color="neutral"
          variant="ghost"
        />

        <UButton
          :to="localePath('/signup')"
          :label="t('nav.signup')"
          trailing-icon="i-lucide-arrow-right"
        />
      </template>
    </UHeader>

    <UMain>
      <NuxtPage />
    </UMain>

    <USeparator icon="i-lucide-sparkles" />

    <UFooter>
      <template #left>
        <p class="text-sm text-muted">
          {{ t('footer.copyright') }} • © {{ new Date().getFullYear() }}
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
