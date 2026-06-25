type EmailAuthMode = 'signup' | 'login' | 'password-reset' | 'password-reset-confirm'

type UseEmailAuthFormOptions = {
  mode: EmailAuthMode
  endpoint: string
  successMessage: string
  errorMessage: string
  resetUid?: string
  resetToken?: string
  clearOnSuccess?: boolean
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
  const config = useRuntimeConfig()

  const form = reactive({
    email: '',
    identifier: '',
    username: '',
    displayName: '',
    password: '',
    passwordConfirmation: '',
    recaptchaToken: ''
  })

  const isSubmitting = shallowRef(false)
  const errorText = shallowRef('')
  const successText = shallowRef('')

  const apiBaseUrl = computed(() => {
    return typeof config.public.apiBaseUrl === 'string'
      ? config.public.apiBaseUrl
      : undefined
  })

  const isSignup = computed(() => options.mode === 'signup')
  const isLogin = computed(() => options.mode === 'login')
  const isPasswordReset = computed(() => options.mode === 'password-reset')
  const isPasswordResetConfirm = computed(() => options.mode === 'password-reset-confirm')

  const signupPasswordRequirements = computed<PasswordRequirement[]>(() => {
    if (!isSignup.value) {
      return []
    }

    return [
      {
        key: 'length',
        message: t('auth.passwordRequirementLength'),
        passes: form.password.length > 8
      },
      {
        key: 'lowercase',
        message: t('auth.passwordRequirementLowercase'),
        passes: /[a-z]/.test(form.password)
      },
      {
        key: 'uppercase',
        message: t('auth.passwordRequirementUppercase'),
        passes: /[A-Z]/.test(form.password)
      },
      {
        key: 'number',
        message: t('auth.passwordRequirementNumber'),
        passes: /\d/.test(form.password)
      },
      {
        key: 'special',
        message: t('auth.passwordRequirementSpecial'),
        passes: /[^A-Za-z0-9]/.test(form.password)
      }
    ]
  })

  const activeSignupPasswordRequirement = computed(() => {
    return signupPasswordRequirements.value.find(requirement => !requirement.passes)
  })

  const signupValidationError = computed(() => {
    if (!isSignup.value) {
      return ''
    }

    if (activeSignupPasswordRequirement.value) {
      return activeSignupPasswordRequirement.value.message
    }

    if (form.password !== form.passwordConfirmation) {
      return t('auth.passwordConfirmationMismatch')
    }

    return ''
  })

  function buildBody() {
    if (isSignup.value) {
      return {
        email: form.email,
        username: form.username,
        display_name: form.displayName,
        password: form.password,
        password_confirmation: form.passwordConfirmation,
        recaptcha_token: form.recaptchaToken
      }
    }

    if (isLogin.value) {
      return {
        identifier: form.identifier,
        password: form.password,
        recaptcha_token: form.recaptchaToken
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
      recaptcha_token: form.recaptchaToken
    }
  }

  function clearFields() {
    form.email = ''
    form.identifier = ''
    form.username = ''
    form.displayName = ''
    form.password = ''
    form.passwordConfirmation = ''
    form.recaptchaToken = ''
  }

  async function submit() {
    errorText.value = ''
    successText.value = ''

    if (signupValidationError.value) {
      errorText.value = signupValidationError.value
      return
    }

    isSubmitting.value = true

    try {
      const response = await $fetch<AuthResponse>(options.endpoint, {
        baseURL: apiBaseUrl.value,
        method: 'POST',
        credentials: 'include',
        body: buildBody()
      })

      successText.value = t(options.successMessage, {
        email: response.account?.email ?? form.email,
        username: response.account?.username ?? form.identifier
      })
      if (options.clearOnSuccess) {
        clearFields()
      }
    } catch {
      errorText.value = t(options.errorMessage)
    } finally {
      isSubmitting.value = false
    }
  }

  return {
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
  }
}
