<script setup lang="ts">
const { locale, locales, setLocale } = useI18n()

const items = computed(() =>
  locales.value.map(item => ({
    label: item.name ?? item.code,
    active: item.code === locale.value,
    onSelect: () => setLocale(item.code)
  }))
)
</script>

<template>
  <UDropdownMenu :items="items">
    <UButton
      color="neutral"
      variant="ghost"
      icon="i-lucide-languages"
      :label="locale.toUpperCase()"
      :aria-label="$t('nav.changeLanguage')"
    />
  </UDropdownMenu>
</template>
