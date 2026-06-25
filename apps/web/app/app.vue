<script setup lang="ts">
const { t, locale, localeProperties } = useI18n()

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
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </UApp>
</template>
