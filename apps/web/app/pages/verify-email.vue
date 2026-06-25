<script setup lang="ts">
definePageMeta({
  layout: 'auth'
})

const route = useRoute()

const email = computed(() => {
  return typeof route.query.email === 'string' ? route.query.email : ''
})
</script>

<template>
  <AuthShell
    title="auth.verificationTitle"
    description="auth.verificationDescription"
  >
    <AuthEmailVerificationForm :initial-email="email" />
  </AuthShell>
</template>
