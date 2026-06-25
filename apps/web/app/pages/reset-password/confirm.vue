<script setup lang="ts">
const route = useRoute()

const resetUid = computed(() => {
  return typeof route.query.uid === 'string' ? route.query.uid : ''
})

const resetToken = computed(() => {
  return typeof route.query.token === 'string' ? route.query.token : ''
})
</script>

<template>
  <AuthPage
    mode="password-reset-confirm"
    title="auth.resetConfirmTitle"
    description="auth.resetConfirmDescription"
    endpoint="/api/auth/password-reset/confirm/"
    input-id="reset-confirm-password"
    submit-label="auth.resetConfirmSubmit"
    success-message="auth.resetConfirmSuccess"
    error-message="auth.resetConfirmError"
    alternate-to="/login"
    alternate-label="auth.loginLink"
    :reset-uid="resetUid"
    :reset-token="resetToken"
    clear-on-success
  />
</template>
