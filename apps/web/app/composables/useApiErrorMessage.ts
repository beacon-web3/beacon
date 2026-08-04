export type ApiErrorPayload = {
  code?: unknown
  detail?: unknown
  email?: unknown
  [key: string]: unknown
}

type ApiErrorShape = {
  data?: unknown
  statusCode?: number
}

type ApiErrorMessageOptions = {
  allowDetail?: boolean
  detailStatusCodes?: readonly number[]
  fallbackMessageKey: string
  networkMessageKey?: string
  safeValidationKeys?: readonly string[]
  tooManyRequestsMessageKey?: string
}

const DEFAULT_SAFE_VALIDATION_KEYS = [
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
  'captcha_token'
] as const

export function useApiErrorMessage() {
  const { t } = useI18n()

  function getApiErrorMessage(error: unknown, options: ApiErrorMessageOptions) {
    const apiError = error as ApiErrorShape
    const {
      allowDetail = false,
      detailStatusCodes = [],
      fallbackMessageKey,
      networkMessageKey = 'auth.networkError',
      safeValidationKeys = DEFAULT_SAFE_VALIDATION_KEYS,
      tooManyRequestsMessageKey = 'auth.tooManyRequestsError'
    } = options

    if (apiError.statusCode === 429) {
      return t(tooManyRequestsMessageKey)
    }

    if (!apiError.statusCode) {
      return t(networkMessageKey)
    }

    const data = getApiErrorData(error)
    const validationMessage = getSafeValidationMessage(data, safeValidationKeys)
    if (validationMessage) {
      return validationMessage
    }

    if (data && (allowDetail || detailStatusCodes.includes(apiError.statusCode))) {
      const detail = getFirstString(data.detail)
      if (detail) {
        return detail
      }
    }

    return t(fallbackMessageKey)
  }

  function getApiErrorData(error: unknown) {
    const data = (error as ApiErrorShape).data
    return isApiErrorPayload(data) ? data : undefined
  }

  return { getApiErrorData, getApiErrorMessage }
}

function getSafeValidationMessage(
  data: ApiErrorPayload | undefined,
  safeValidationKeys: readonly string[]
) {
  if (!data) {
    return undefined
  }

  for (const key of safeValidationKeys) {
    const message = getFirstString(data[key])
    if (message) {
      return message
    }
  }

  return undefined
}

function isApiErrorPayload(value: unknown): value is ApiErrorPayload {
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
