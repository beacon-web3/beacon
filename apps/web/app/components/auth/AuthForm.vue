<script setup lang="ts">
const props = defineProps<{
  mode: 'signup' | 'login' | 'password-reset' | 'password-reset-confirm'
  endpoint: string
  inputId: string
  submitLabel: string
  successMessage: string
  errorMessage: string
  alternateTo: string
  alternateLabel: string
  resetUid?: string
  resetToken?: string
  clearOnSuccess?: boolean
  socialAuthError?: string
  socialAuthSubmitting?: boolean
}>()

const emit = defineEmits<{
  verificationRequired: [email: string]
  googleAuthStart: []
}>()

const { t } = useI18n()
const localePath = useLocalePath()
const showPassword = shallowRef(false)
const showPasswordConfirmation = shallowRef(false)
const captchaEnabled = useRuntimeConfig().public.captchaEnabled

const {
  form,
  schema,
  isSubmitting,
  errorText,
  successText,
  isSignup,
  isLogin,
  isPasswordReset,
  isPasswordResetConfirm,
  activeSignupPasswordRequirement,
  submit
} = useEmailAuthForm({
  ...props,
  onVerificationRequired: email => emit('verificationRequired', email)
})
</script>

<template>
  <UForm
    :schema="schema"
    :state="form"
    class="mt-6 space-y-5"
    @submit="submit"
  >
    <UFormField
      v-if="isSignup"
      :label="t('auth.displayNameLabel')"
      name="displayName"
    >
      <UInput
        id="signup-display-name"
        v-model="form.displayName"
        name="display_name"
        type="text"
        required
        autocomplete="name"
        size="xl"
        :placeholder="t('auth.displayNamePlaceholder')"
        class="w-full"
      />
    </UFormField>

    <UFormField
      v-if="isSignup"
      :label="t('auth.usernameLabel')"
      name="username"
    >
      <UInput
        id="signup-username"
        v-model="form.username"
        name="username"
        type="text"
        required
        autocomplete="username"
        size="xl"
        :placeholder="t('auth.usernamePlaceholder')"
        class="w-full"
      />
    </UFormField>

    <UFormField
      v-if="isSignup || isPasswordReset"
      :label="t('auth.emailLabel')"
      name="email"
    >
      <UInput
        :id="inputId"
        v-model="form.email"
        name="email"
        type="email"
        required
        autocomplete="email"
        size="xl"
        :placeholder="t('auth.emailPlaceholder')"
        class="w-full"
      />
    </UFormField>

    <UFormField
      v-if="isLogin"
      :label="t('auth.identifierLabel')"
      name="identifier"
    >
      <UInput
        :id="inputId"
        v-model="form.identifier"
        name="identifier"
        type="text"
        required
        autocomplete="username"
        size="xl"
        :placeholder="t('auth.identifierPlaceholder')"
        class="w-full"
      />
    </UFormField>

    <UFormField
      v-if="isSignup || isLogin || isPasswordResetConfirm"
      :label="isPasswordResetConfirm ? t('auth.newPasswordLabel') : t('auth.passwordLabel')"
      name="password"
      :help="(isSignup || isPasswordResetConfirm) && !successText ? activeSignupPasswordRequirement?.message : undefined"
    >
      <UInput
        id="auth-password"
        v-model="form.password"
        name="password"
        :type="showPassword ? 'text' : 'password'"
        required
        :autocomplete="isLogin ? 'current-password' : 'new-password'"
        size="xl"
        :placeholder="isPasswordResetConfirm ? t('auth.newPasswordPlaceholder') : t('auth.passwordPlaceholder')"
        :ui="{ trailing: 'pe-1' }"
        class="w-full"
      >
        <template #trailing>
          <UButton
            color="neutral"
            variant="link"
            size="sm"
            :icon="showPassword ? 'i-lucide-eye-off' : 'i-lucide-eye'"
            :aria-label="showPassword ? t('auth.hidePassword') : t('auth.showPassword')"
            :aria-pressed="showPassword"
            aria-controls="auth-password"
            @click="showPassword = !showPassword"
          />
        </template>
      </UInput>
    </UFormField>

    <UFormField
      v-if="isSignup"
      :label="t('auth.passwordConfirmationLabel')"
      name="passwordConfirmation"
    >
      <UInput
        id="auth-password-confirmation"
        v-model="form.passwordConfirmation"
        name="password_confirmation"
        :type="showPasswordConfirmation ? 'text' : 'password'"
        required
        autocomplete="new-password"
        size="xl"
        :placeholder="t('auth.passwordConfirmationPlaceholder')"
        :ui="{ trailing: 'pe-1' }"
        class="w-full"
      >
        <template #trailing>
          <UButton
            color="neutral"
            variant="link"
            size="sm"
            :icon="showPasswordConfirmation ? 'i-lucide-eye-off' : 'i-lucide-eye'"
            :aria-label="showPasswordConfirmation ? t('auth.hidePassword') : t('auth.showPassword')"
            :aria-pressed="showPasswordConfirmation"
            aria-controls="auth-password-confirmation"
            @click="showPasswordConfirmation = !showPasswordConfirmation"
          />
        </template>
      </UInput>
    </UFormField>

    <p
      v-if="isPasswordReset || isPasswordResetConfirm"
      class="text-sm leading-6 text-ink-muted"
    >
      {{ t('auth.passwordResetHelp') }}
    </p>

    <p
      v-if="captchaEnabled"
      class="text-xs leading-5 text-ink-faint"
    >
      {{ t('auth.captchaNotice') }}
    </p>

    <UAlert
      v-if="successText"
      role="status"
      color="success"
      variant="soft"
      :title="successText"
    />
    <UAlert
      v-if="errorText"
      role="alert"
      color="error"
      variant="soft"
      :title="errorText"
    />

    <div class="grid gap-3">
      <UButton
        type="submit"
        :loading="isSubmitting"
        :disabled="isSubmitting"
        :label="isSubmitting ? t('auth.submitting') : t(submitLabel)"
        color="primary"
        size="xl"
        trailing-icon="i-lucide-arrow-right"
        block
      />
      <UButton
        :to="localePath(alternateTo)"
        :label="t(alternateLabel)"
        variant="ghost"
        color="neutral"
        size="lg"
        block
      />
      <UButton
        v-if="isLogin"
        :to="localePath('/reset-password')"
        :label="t('auth.forgotPasswordLink')"
        variant="link"
        color="neutral"
        size="sm"
        block
      />
    </div>
  </UForm>
</template>

<style>
input[type='password']::-ms-reveal {
  display: none;
}
</style>
