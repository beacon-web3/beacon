<script setup lang="ts">
definePageMeta({
  layout: 'auth'
})

const localePath = useLocalePath()
const route = useRoute()
const { t } = useI18n()
const {
  isStartingGoogleAuth,
  socialAuthError,
  startGoogleAuth
} = useSocialAuthStart()

const socialErrorText = computed(() => {
  if (socialAuthError.value) {
    return socialAuthError.value
  }

  return route.query.error === 'social_auth_failed'
    ? t('auth.socialCallbackError')
    : ''
})

async function goToVerification(email: string) {
  await navigateTo(`${localePath('/verify-email')}?email=${encodeURIComponent(email)}`)
}

async function startGoogleLogin() {
  await startGoogleAuth({ next: '/dashboard' })
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
    :social-auth-error="socialErrorText"
    :social-auth-submitting="isStartingGoogleAuth"
    @verification-required="goToVerification"
    @google-auth-start="startGoogleLogin"
  />
</template>
