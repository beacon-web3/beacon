<script setup lang="ts">
definePageMeta({
  layout: 'auth'
})

const localePath = useLocalePath()

async function goToVerification(email: string) {
  await navigateTo(`${localePath('/verify-email')}?email=${encodeURIComponent(email)}`)
}
</script>

<template>
  <AuthScreen
    mode="login"
    title="auth.loginTitle"
    description="auth.loginDescription"
    endpoint="/api/auth/login/"
    input-id="login-email"
    submit-label="auth.loginSubmit"
    success-message="auth.loginSuccess"
    error-message="auth.loginError"
    alternate-to="/signup"
    alternate-label="auth.signupLink"
    @verification-required="goToVerification"
  />
</template>
