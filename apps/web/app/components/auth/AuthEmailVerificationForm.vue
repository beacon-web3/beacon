<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import * as z from 'zod'

const props = defineProps<{
  initialEmail: string
}>()

type VerificationFormState = {
  email: string
  otp: number[]
}

type AccountResponse = {
  account?: {
    email: string
  }
}

const { t } = useI18n()
const localePath = useLocalePath()
const { apiFetch } = useApiFetch()
const { getApiErrorMessage } = useApiErrorMessage()
const { executeCaptcha } = useCapToken()

const form = reactive<VerificationFormState>({
  email: props.initialEmail,
  otp: []
})

const isSubmitting = shallowRef(false)
const isResending = shallowRef(false)
const successText = shallowRef('')
const errorText = shallowRef('')
const resendText = shallowRef('')

const otpCode = computed(() => form.otp.join(''))

const schema = computed(() => {
  return z.object({
    email: z.string().min(1, t('auth.fieldRequired')).email(t('auth.emailInvalid')),
    otp: z.array(z.number()).length(6, t('auth.verificationCodeInvalid'))
  })
})

watch(
  () => props.initialEmail,
  (email) => {
    if (!form.email) {
      form.email = email
    }
  }
)

async function submit(_event: FormSubmitEvent<VerificationFormState>) {
  successText.value = ''
  errorText.value = ''

  isSubmitting.value = true
  try {
    const response = await apiFetch<AccountResponse>('/api/auth/email-verification/confirm/', {
      method: 'POST',
      body: {
        email: form.email,
        otp: otpCode.value
      }
    })

    successText.value = t('auth.verificationSuccess', {
      email: response.account?.email ?? form.email
    })
    form.otp = []
  } catch (error) {
    errorText.value = getApiErrorMessage(error, { fallbackMessageKey: 'auth.verificationError' })
  } finally {
    isSubmitting.value = false
  }
}

async function resendCode() {
  successText.value = ''
  errorText.value = ''
  resendText.value = ''

  if (!schema.value.shape.email.safeParse(form.email).success) {
    errorText.value = t('auth.emailInvalid')
    return
  }

  isResending.value = true
  try {
    const captchaToken = await executeCaptcha()

    await apiFetch('/api/auth/email-verification/request/', {
      method: 'POST',
      body: {
        email: form.email,
        captcha_token: captchaToken
      }
    })

    resendText.value = t('auth.verificationResendSuccess')
  } catch (error) {
    errorText.value = getApiErrorMessage(error, { fallbackMessageKey: 'auth.verificationResendError' })
  } finally {
    isResending.value = false
  }
}
</script>

<template>
  <UForm
    :schema="schema"
    :state="form"
    class="mt-6 space-y-5"
    @submit="submit"
  >
    <UFormField
      :label="t('auth.emailLabel')"
      name="email"
    >
      <UInput
        id="verification-email"
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
      :label="t('auth.verificationCodeLabel')"
      name="otp"
      :help="t('auth.verificationCodeHelp')"
    >
      <UPinInput
        id="verification-code"
        v-model="form.otp"
        name="otp"
        type="number"
        required
        otp
        :length="6"
        placeholder="0"
        size="xl"
        :disabled="isSubmitting || isResending"
      />
    </UFormField>

    <UAlert
      v-if="successText"
      role="status"
      color="success"
      variant="soft"
      :title="successText"
    />
    <UAlert
      v-if="resendText"
      role="status"
      color="success"
      variant="soft"
      :title="resendText"
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
        :disabled="isSubmitting || isResending"
        :label="isSubmitting ? t('auth.submitting') : t('auth.verificationSubmit')"
        color="primary"
        size="xl"
        trailing-icon="i-lucide-check-circle"
        block
      />
      <UButton
        type="button"
        :loading="isResending"
        :disabled="isSubmitting || isResending"
        :label="isResending ? t('auth.submitting') : t('auth.verificationResend')"
        variant="soft"
        color="neutral"
        size="lg"
        block
        @click="resendCode"
      />
      <UButton
        :to="localePath('/login')"
        :label="t('auth.loginLink')"
        variant="ghost"
        color="neutral"
        size="lg"
        block
      />
    </div>
  </UForm>
</template>
