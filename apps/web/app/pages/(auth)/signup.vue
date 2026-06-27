<script setup lang="ts">
definePageMeta({
  layout: 'auth'
})

const localePath = useLocalePath()
const {
  isStartingGoogleAuth,
  socialAuthError,
  startGoogleAuth
} = useSocialAuthStart()

async function goToVerification(email: string) {
  await navigateTo(`${localePath('/verify-email')}?email=${encodeURIComponent(email)}`)
}

async function startGoogleSignup() {
  await startGoogleAuth({ next: '/dashboard' })
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
    :social-auth-error="socialAuthError"
    :social-auth-submitting="isStartingGoogleAuth"
    @verification-required="goToVerification"
    @google-auth-start="startGoogleSignup"
  />
</template>
