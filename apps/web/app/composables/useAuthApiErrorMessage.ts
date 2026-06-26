type AuthApiErrorPayload = {
  code?: unknown
  detail?: unknown
  email?: unknown
  [key: string]: unknown
}

type AuthApiErrorShape = {
  data?: unknown
  statusCode?: number
}

const SAFE_VALIDATION_KEYS = [
  'non_field_errors',
  'email',
  'username',
  'display_name',
  'password',
  'password_confirmation',
  'identifier',
  'otp',
  'uid',
  'token',
  'recaptcha_token'
]

export function useAuthApiErrorMessage() {
  const { t } = useI18n()

  function getAuthApiErrorMessage(error: unknown, fallbackMessageKey: string) {
    const apiError = error as AuthApiErrorShape

    if (apiError.statusCode === 429) {
      return t('auth.tooManyRequestsError')
    }

    if (!apiError.statusCode) {
      return t('auth.networkError')
    }

    return getSafeValidationMessage(apiError.data) ?? t(fallbackMessageKey)
  }

  function getVerificationRequiredEmail(error: unknown) {
    const data = (error as AuthApiErrorShape).data
    if (!isAuthApiErrorPayload(data)) {
      return undefined
    }

    return data.code === 'EMAIL_VERIFICATION_REQUIRED' && typeof data.email === 'string'
      ? data.email
      : undefined
  }

  return { getAuthApiErrorMessage, getVerificationRequiredEmail }
}

function getSafeValidationMessage(data: unknown) {
  if (!isAuthApiErrorPayload(data)) {
    return undefined
  }

  for (const key of SAFE_VALIDATION_KEYS) {
    const message = getFirstString(data[key])
    if (message) {
      return message
    }
  }

  return getFirstString(data.detail)
}

function isAuthApiErrorPayload(value: unknown): value is AuthApiErrorPayload {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function getFirstString(value: unknown): string | undefined {
  if (typeof value === 'string') {
    return value
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      const message = getFirstString(item)
      if (message) {
        return message
      }
    }
  }

  return undefined
}
