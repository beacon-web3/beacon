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
    mode="signup"
    title="auth.signupTitle"
    description="auth.signupDescription"
    endpoint="/api/auth/signup/"
    input-id="signup-email"
    submit-label="auth.signupSubmit"
    success-message="auth.signupSuccess"
    error-message="auth.signupError"
    alternate-to="/login"
    alternate-label="auth.loginLink"
    clear-on-success
    @verification-required="goToVerification"
  />
</template>
