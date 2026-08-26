import type { FormSubmitEvent } from '@nuxt/ui'
import * as z from 'zod'

type EmailAuthMode = 'signup' | 'login' | 'password-reset' | 'password-reset-confirm'

type EmailAuthFormState = {
  email: string
  identifier: string
  username: string
  displayName: string
  password: string
  passwordConfirmation: string
  captchaToken: string
}

type EmailAuthFormData = Partial<EmailAuthFormState>

type UseEmailAuthFormOptions = {
  mode: EmailAuthMode
  endpoint: string
  successMessage: string
  errorMessage: string
  resetUid?: string
  resetToken?: string
  clearOnSuccess?: boolean
  onVerificationRequired?: (email: string) => void | Promise<void>
}

type AuthResponse = {
  account?: {
    id: number
    email: string
    username: string
    display_name: string
  }
}

type PasswordRequirement = {
  key: string
  message: string
  passes: boolean
}

export function useEmailAuthForm(options: UseEmailAuthFormOptions) {
  const { t } = useI18n()
  const { apiFetch } = useApiFetch()
  const { getApiErrorData, getApiErrorMessage } = useApiErrorMessage()
  const { executeCaptcha } = useCapToken()
  const accountStore = useAccountStore()

  const form = reactive<EmailAuthFormState>({
    email: '',
    identifier: '',
    username: '',
    displayName: '',
    password: '',
    passwordConfirmation: '',
    captchaToken: ''
  })

  const isSubmitting = shallowRef(false)
  const errorText = shallowRef('')
  const successText = shallowRef('')

  const isSignup = computed(() => options.mode === 'signup')
  const isLogin = computed(() => options.mode === 'login')
  const isPasswordReset = computed(() => options.mode === 'password-reset')
  const isPasswordResetConfirm = computed(() => options.mode === 'password-reset-confirm')

  function getSignupPasswordRequirements(password: string): PasswordRequirement[] {
    return [
      {
        key: 'length',
        message: t('auth.passwordRequirementLength'),
        passes: password.length > 8
      },
      {
        key: 'lowercase',
        message: t('auth.passwordRequirementLowercase'),
        passes: /[a-z]/.test(password)
      },
      {
        key: 'uppercase',
        message: t('auth.passwordRequirementUppercase'),
        passes: /[A-Z]/.test(password)
      },
      {
        key: 'number',
        message: t('auth.passwordRequirementNumber'),
        passes: /\d/.test(password)
      },
      {
        key: 'special',
        message: t('auth.passwordRequirementSpecial'),
        passes: /[^A-Za-z0-9]/.test(password)
      }
    ]
  }

  const passwordRequirements = computed<PasswordRequirement[]>(() => {
    if (!isSignup.value && !isPasswordResetConfirm.value) {
      return []
    }

    return getSignupPasswordRequirements(form.password)
  })

  const activeSignupPasswordRequirement = computed(() => {
    return passwordRequirements.value.find(requirement => !requirement.passes)
  })

  const requiredString = computed(() => {
    return z.string().min(1, t('auth.fieldRequired'))
  })

  const emailString = computed(() => {
    return requiredString.value.email(t('auth.emailInvalid'))
  })

  const signupPasswordString = computed(() => {
    return requiredString.value.superRefine((password, context) => {
      const failedRequirement = getSignupPasswordRequirements(password).find(
        requirement => !requirement.passes
      )

      if (failedRequirement) {
        context.addIssue({
          code: 'custom',
          message: failedRequirement.message
        })
      }
    })
  })

  const schema = computed(() => {
    if (isSignup.value) {
      return z.object({
        displayName: requiredString.value,
        username: requiredString.value,
        email: emailString.value,
        password: signupPasswordString.value,
        passwordConfirmation: requiredString.value,
        captchaToken: z.string().optional()
      }).refine(data => data.password === data.passwordConfirmation, {
        path: ['passwordConfirmation'],
        message: t('auth.passwordConfirmationMismatch')
      })
    }

    if (isLogin.value) {
      return z.object({
        identifier: requiredString.value,
        password: requiredString.value,
        captchaToken: z.string().optional()
      })
    }

    if (isPasswordResetConfirm.value) {
      return z.object({
        password: signupPasswordString.value
      })
    }

    return z.object({
      email: emailString.value,
      captchaToken: z.string().optional()
    })
  })

  function buildBody() {
    if (isSignup.value) {
      return {
        email: form.email,
        username: form.username,
        display_name: form.displayName,
        password: form.password,
        password_confirmation: form.passwordConfirmation,
        captcha_token: form.captchaToken
      }
    }

    if (isLogin.value) {
      return {
        identifier: form.identifier,
        password: form.password,
        captcha_token: form.captchaToken
      }
    }

    if (isPasswordResetConfirm.value) {
      return {
        uid: options.resetUid,
        token: options.resetToken,
        password: form.password
      }
    }

    return {
      email: form.email,
      captcha_token: form.captchaToken
    }
  }

  function clearFields() {
    form.email = ''
    form.identifier = ''
    form.username = ''
    form.displayName = ''
    form.password = ''
    form.passwordConfirmation = ''
    form.captchaToken = ''
  }

  function getVerificationRequiredEmail(error: unknown) {
    const data = getApiErrorData(error)
    return data?.code === 'EMAIL_VERIFICATION_REQUIRED' && typeof data.email === 'string'
      ? data.email
      : undefined
  }

  async function submit(_event: FormSubmitEvent<EmailAuthFormData>) {
    errorText.value = ''
    successText.value = ''

    isSubmitting.value = true

    try {
      if (!isPasswordResetConfirm.value) {
        form.captchaToken = await executeCaptcha()
      }

      const response = await apiFetch<AuthResponse>(options.endpoint, {
        method: 'POST',
        body: buildBody()
      })

      successText.value = t(options.successMessage, {
        email: response.account?.email ?? form.email,
        username: response.account?.username ?? form.identifier
      })
      if (isLogin.value) {
        await accountStore.fetchAccount()
        await navigateTo('/dashboard')
      }
      if (options.clearOnSuccess) {
        clearFields()
      }
      if (isSignup.value && response.account?.email) {
        await options.onVerificationRequired?.(response.account.email)
      }
    } catch (error) {
      const verificationEmail = getVerificationRequiredEmail(error)
      if (verificationEmail) {
        await options.onVerificationRequired?.(verificationEmail)
        return
      }

      errorText.value = getApiErrorMessage(error, { fallbackMessageKey: options.errorMessage })
    } finally {
      isSubmitting.value = false
    }
  }

  return {
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
  }
}
