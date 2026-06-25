<script setup lang="ts">
const props = defineProps<{
  mode: 'signup' | 'login' | 'password-reset' | 'password-reset-confirm'
  title: string
  description: string
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
}>()

const { t } = useI18n()
const localePath = useLocalePath()

const {
  form,
  isSubmitting,
  errorText,
  successText,
  isSignup,
  isLogin,
  isPasswordReset,
  isPasswordResetConfirm,
  activeSignupPasswordRequirement,
  submit
} = useEmailAuthForm(props)
</script>

<template>
  <div class="beacon-container py-16 sm:py-24">
    <section class="grid min-h-[calc(100vh-13rem)] gap-10 lg:grid-cols-[minmax(0,0.82fr)_minmax(22rem,0.58fr)] lg:items-center">
      <EmailAuthContextPanel
        :title="title"
        :description="description"
      />

      <div class="beacon-panel p-5 sm:p-6">
        <div class="flex items-start justify-between gap-5 border-b border-rule pb-5">
          <div>
            <p class="beacon-kicker">
              {{ t('auth.panelEyebrow') }}
            </p>
            <h2 class="mt-2 text-2xl font-semibold tracking-[-0.04em] text-ink">
              {{ t('auth.panelTitle') }}
            </h2>
          </div>
          <UIcon
            name="i-lucide-mail-plus"
            class="size-6 shrink-0 text-beacon-600 dark:text-beacon-300"
          />
        </div>

        <form
          class="mt-6 space-y-5"
          @submit.prevent="submit"
        >
          <div v-if="isSignup">
            <label
              for="signup-display-name"
              class="block text-sm font-semibold text-ink"
            >
              {{ t('auth.displayNameLabel') }}
            </label>
            <input
              id="signup-display-name"
              v-model="form.displayName"
              name="display_name"
              type="text"
              required
              autocomplete="name"
              :placeholder="t('auth.displayNamePlaceholder')"
              class="mt-2 w-full rounded-xl border border-rule bg-paper px-4 py-3 text-ink outline-none transition placeholder:text-ink-faint focus:border-beacon-500 focus:ring-4 focus:ring-beacon-300/20"
            >
          </div>

          <div v-if="isSignup">
            <label
              for="signup-username"
              class="block text-sm font-semibold text-ink"
            >
              {{ t('auth.usernameLabel') }}
            </label>
            <input
              id="signup-username"
              v-model="form.username"
              name="username"
              type="text"
              required
              autocomplete="username"
              :placeholder="t('auth.usernamePlaceholder')"
              class="mt-2 w-full rounded-xl border border-rule bg-paper px-4 py-3 text-ink outline-none transition placeholder:text-ink-faint focus:border-beacon-500 focus:ring-4 focus:ring-beacon-300/20"
            >
          </div>

          <div v-if="isSignup || isPasswordReset">
            <label
              :for="inputId"
              class="block text-sm font-semibold text-ink"
            >
              {{ t('auth.emailLabel') }}
            </label>
            <input
              :id="inputId"
              v-model="form.email"
              name="email"
              type="email"
              required
              autocomplete="email"
              :placeholder="t('auth.emailPlaceholder')"
              class="mt-2 w-full rounded-xl border border-rule bg-paper px-4 py-3 text-ink outline-none transition placeholder:text-ink-faint focus:border-beacon-500 focus:ring-4 focus:ring-beacon-300/20"
            >
          </div>

          <div v-if="isLogin">
            <label
              :for="inputId"
              class="block text-sm font-semibold text-ink"
            >
              {{ t('auth.identifierLabel') }}
            </label>
            <input
              :id="inputId"
              v-model="form.identifier"
              name="identifier"
              type="text"
              required
              autocomplete="username"
              :placeholder="t('auth.identifierPlaceholder')"
              class="mt-2 w-full rounded-xl border border-rule bg-paper px-4 py-3 text-ink outline-none transition placeholder:text-ink-faint focus:border-beacon-500 focus:ring-4 focus:ring-beacon-300/20"
            >
          </div>

          <div v-if="isSignup || isLogin || isPasswordResetConfirm">
            <label
              for="auth-password"
              class="block text-sm font-semibold text-ink"
            >
              {{ isPasswordResetConfirm ? t('auth.newPasswordLabel') : t('auth.passwordLabel') }}
            </label>
            <input
              id="auth-password"
              v-model="form.password"
              name="password"
              type="password"
              required
              :autocomplete="isLogin ? 'current-password' : 'new-password'"
              :placeholder="isPasswordResetConfirm ? t('auth.newPasswordPlaceholder') : t('auth.passwordPlaceholder')"
              class="mt-2 w-full rounded-xl border border-rule bg-paper px-4 py-3 text-ink outline-none transition placeholder:text-ink-faint focus:border-beacon-500 focus:ring-4 focus:ring-beacon-300/20"
            >
          </div>

          <div v-if="isSignup">
            <label
              for="auth-password-confirmation"
              class="block text-sm font-semibold text-ink"
            >
              {{ t('auth.passwordConfirmationLabel') }}
            </label>
            <input
              id="auth-password-confirmation"
              v-model="form.passwordConfirmation"
              name="password_confirmation"
              type="password"
              required
              autocomplete="new-password"
              :placeholder="t('auth.passwordConfirmationPlaceholder')"
              class="mt-2 w-full rounded-xl border border-rule bg-paper px-4 py-3 text-ink outline-none transition placeholder:text-ink-faint focus:border-beacon-500 focus:ring-4 focus:ring-beacon-300/20"
            >
          </div>

          <p
            v-if="activeSignupPasswordRequirement && !successText"
            role="status"
            aria-label="Password requirement"
            class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-medium text-amber-900 dark:border-amber-900/70 dark:bg-amber-950/30 dark:text-amber-200"
          >
            {{ activeSignupPasswordRequirement.message }}
          </p>

          <p
            v-if="isPasswordReset || isPasswordResetConfirm"
            class="text-sm leading-6 text-ink-muted"
          >
            {{ t('auth.passwordResetHelp') }}
          </p>

          <p class="text-xs leading-5 text-ink-faint">
            {{ t('auth.recaptchaNotice') }}
          </p>

          <p
            v-if="successText"
            role="status"
            class="rounded-xl border border-reputation/25 bg-reputation-muted px-4 py-3 text-sm font-medium text-ink"
          >
            {{ successText }}
          </p>
          <p
            v-if="errorText"
            role="alert"
            class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700 dark:border-red-900/70 dark:bg-red-950/30 dark:text-red-300"
          >
            {{ errorText }}
          </p>

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
        </form>
      </div>
    </section>
  </div>
</template>
